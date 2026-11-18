"""GOODZ landing page and deliberately small authenticated CMS."""
from __future__ import annotations

import hashlib
import hmac
import io
import json
import os
import re
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager, asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps, UnidentifiedImageError
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / 'static'
MAX_UPLOAD = 8 * 1024 * 1024
SESSION_AGE = 60 * 60 * 12
CATEGORIES = {'pastelaria', 'dogueria'}
IMAGE_KEYS = {'logo_goodz', 'logo_pastelaria', 'logo_dogueria', 'hero_image', 'pastelaria_image', 'dogueria_image'}
LINK_KEYS = {'ifood_url', 'food99_url', 'instagram_url', 'tiktok_url', 'whatsapp_url'}
TEXT_KEYS = {'hero_title', 'hero_description', 'pastelaria_title', 'pastelaria_description', 'dogueria_title', 'dogueria_description', 'about_text', 'address_text'}
DEFAULTS = {
    'logo_goodz': '/assets/logo-goodz.webp',
    'logo_pastelaria': '/assets/logo-pastelaria.webp',
    'logo_dogueria': '/assets/logo-dogueria.webp',
    'hero_image': '/assets/store-showcase.webp',
    'pastelaria_image': '/assets/pastel-showcase.webp',
    'dogueria_image': '/assets/dog-showcase.webp',
    'hero_title': 'Sabor que merece destaque.',
    'hero_description': 'Um universo de sabores. Duas especialidades, uma só assinatura: GOODZ.',
    'pastelaria_title': 'Crocância que conquista.',
    'pastelaria_description': 'Pastéis feitos para transformar qualquer pausa em um grande momento.',
    'dogueria_title': 'O hot dog ganha uma nova atitude.',
    'dogueria_description': 'Uma nova experiência GOODZ para os apaixonados por hot dogs.',
    'about_text': 'GOODZ reúne dois jeitos de aproveitar o que há de melhor em comida cheia de personalidade.',
    'address_text': 'Salto, São Paulo',
    'ifood_url': '', 'food99_url': '', 'instagram_url': '', 'tiktok_url': '', 'whatsapp_url': '',
}

@contextmanager
def connect(path: Path):
    c = sqlite3.connect(path, timeout=15)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()

def init_db(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as c:
        c.execute('PRAGMA journal_mode=WAL')
        c.executescript('''
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY, category TEXT NOT NULL CHECK(category IN ('pastelaria','dogueria')),
                name TEXT NOT NULL, description TEXT NOT NULL, price_cents INTEGER,
                image_url TEXT NOT NULL, visible INTEGER NOT NULL DEFAULT 1,
                sort_order INTEGER NOT NULL DEFAULT 0, created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS admin_auth (id INTEGER PRIMARY KEY CHECK(id=1), password_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, csrf_token TEXT NOT NULL, expires_at INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS login_attempts (id INTEGER PRIMARY KEY, ip TEXT NOT NULL, at INTEGER NOT NULL);
            CREATE INDEX IF NOT EXISTS attempts_ip_at ON login_attempts(ip,at);
        ''')
        for key, value in DEFAULTS.items():
            c.execute('INSERT OR IGNORE INTO settings(key,value) VALUES (?,?)', (key, value))

def password_hash(password: str) -> str:
    if len(password) < 12 or len(password) > 256:
        raise ValueError('A senha deve ter entre 12 e 256 caracteres.')
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f'scrypt$16384$8$1${salt.hex()}${digest.hex()}'

def verify_password(password: str, stored: str) -> bool:
    try:
        algo, n, r, p, salt, digest = stored.split('$')
        if algo != 'scrypt':
            return False
        calc = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(calc, bytes.fromhex(digest))
    except (ValueError, TypeError, OverflowError):
        return False

def valid_url(value: str) -> bool:
    if value == '':
        return True
    if len(value) > 600 or any(ch.isspace() for ch in value):
        return False
    try:
        parts = urlsplit(value)
        hostname = parts.hostname
        port = parts.port  # Access validates that any explicit port is numeric and in range.
    except ValueError:
        return False
    return (parts.scheme in {'http', 'https'} and bool(hostname)
            and parts.username is None and parts.password is None
            and (port is None or port > 0))

def image_url(value: str) -> bool:
    return value.startswith('/assets/') or bool(re.fullmatch(r'/uploads/[a-f0-9]{32}\.webp', value))

class LoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=512)
class SettingsRequest(BaseModel):
    values: dict[str, str]
class ProductRequest(BaseModel):
    category: str
    name: str = Field(min_length=1, max_length=90)
    description: str = Field(default='', max_length=400)
    price_cents: int | None = Field(default=None, ge=0, le=99999999)
    image_url: str = Field(default='')
    visible: bool = True
    sort_order: int = Field(default=0, ge=-100000, le=100000)
class PasswordRequest(BaseModel):
    current_password: str
    new_password: str

def create_app(data_path: Path | None = None) -> FastAPI:
    data = Path(data_path or os.environ.get('GOODZ_DATA_DIR', str(ROOT / 'data'))).resolve()
    uploads = data / 'uploads'
    uploads.mkdir(parents=True, exist_ok=True)
    database = data / 'goodz.sqlite3'

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(database)
        yield

    app = FastAPI(title='GOODZ Site', docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.mount('/assets', StaticFiles(directory=STATIC / 'assets'), name='assets')
    app.mount('/uploads', StaticFiles(directory=uploads), name='uploads')
    app.mount('/styles', StaticFiles(directory=STATIC / 'styles'), name='styles')
    app.mount('/scripts', StaticFiles(directory=STATIC / 'scripts'), name='scripts')

    @app.middleware('http')
    async def secure_headers(request: Request, call_next):
        response = None
        if request.method == 'POST' and request.url.path == '/api/admin/upload':
            # Authenticate before Starlette parses multipart input into temporary files.
            # Require a bounded body even before image decoding; the reverse proxy
            # must apply an independent upload limit as defense in depth.
            try:
                current_session(request, csrf=True)
            except HTTPException as error:
                response = JSONResponse({'detail': error.detail}, status_code=error.status_code)
            if response is None:
                length = request.headers.get('content-length')
                try:
                    declared = int(length) if length is not None else -1
                except ValueError:
                    declared = -1
                if declared < 0 or request.headers.get('transfer-encoding'):
                    response = JSONResponse({'detail': 'Tamanho do envio obrigatório.'}, status_code=411)
                elif declared > MAX_UPLOAD + 128 * 1024:
                    response = JSONResponse({'detail': 'Arquivo excede o limite de envio.'}, status_code=413)
        if response is None:
            response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'self'"
        if request.url.path.startswith('/api/admin') or request.url.path == '/admin':
            response.headers['Cache-Control'] = 'no-store'
        return response

    def current_session(request: Request, csrf: bool = False):
        token = request.cookies.get('goodz_session', '')
        if not token:
            raise HTTPException(401, 'Faça login para continuar.')
        with connect(database) as c:
            row = c.execute('SELECT csrf_token,expires_at FROM sessions WHERE token_hash=?', (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
        if not row or row['expires_at'] <= int(time.time()):
            raise HTTPException(401, 'Sessão expirada.')
        if csrf:
            if not hmac.compare_digest(request.headers.get('x-csrf-token', ''), row['csrf_token']):
                raise HTTPException(403, 'Token CSRF inválido.')
            origin = request.headers.get('origin') or request.headers.get('referer')
            expected_scheme = 'https' if os.environ.get('COOKIE_SECURE') == '1' else request.url.scheme
            if origin:
                try:
                    parsed_origin = urlsplit(origin)
                except ValueError:
                    raise HTTPException(403, 'Origem não permitida.') from None
                if (parsed_origin.scheme != expected_scheme
                        or parsed_origin.netloc != request.headers.get('host')):
                    raise HTTPException(403, 'Origem não permitida.')
        return row

    def read_settings():
        with connect(database) as c:
            return {r['key']: r['value'] for r in c.execute('SELECT key,value FROM settings')}

    def read_products(public: bool):
        with connect(database) as c:
            where = 'WHERE visible=1' if public else ''
            return [dict(r) | {'visible': bool(r['visible'])} for r in c.execute(f'SELECT * FROM products {where} ORDER BY category,sort_order,created_at', ())]

    @app.get('/')
    def home():
        return FileResponse(STATIC / 'index.html')

    @app.get('/admin')
    def admin_page():
        return FileResponse(STATIC / 'admin.html')

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    @app.get('/api/site')
    def public_content():
        return {'settings': read_settings(), 'products': read_products(True)}

    @app.post('/api/admin/login')
    def login(payload: LoginRequest, request: Request, response: Response):
        ip = request.client.host if request.client else 'unknown'
        now = int(time.time())
        with connect(database) as c:
            c.execute('DELETE FROM login_attempts WHERE at<?', (now-900,))
            count = c.execute('SELECT count(*) FROM login_attempts WHERE ip=?', (ip,)).fetchone()[0]
            if count >= 6:
                raise HTTPException(429, 'Muitas tentativas. Tente novamente em 15 minutos.')
            saved = c.execute('SELECT password_hash FROM admin_auth WHERE id=1').fetchone()
            valid = bool(saved) and verify_password(payload.password, saved['password_hash'])
            if not valid:
                c.execute('INSERT INTO login_attempts(ip,at) VALUES(?,?)', (ip, now))
            else:
                c.execute('DELETE FROM login_attempts WHERE ip=?', (ip,))
                c.execute('DELETE FROM sessions WHERE expires_at<=?', (now,))
                token = secrets.token_urlsafe(32)
                csrf = secrets.token_urlsafe(32)
                c.execute('INSERT INTO sessions(token_hash,csrf_token,expires_at) VALUES (?,?,?)', (hashlib.sha256(token.encode()).hexdigest(), csrf, now + SESSION_AGE))
        if not valid:
            raise HTTPException(401, 'Credenciais inválidas ou senha ainda não configurada.')
        response.set_cookie('goodz_session', token, httponly=True, secure=os.environ.get('COOKIE_SECURE') == '1', samesite='strict', max_age=SESSION_AGE)
        return {'csrf': csrf}

    @app.get('/api/admin/state')
    def admin_state(request: Request):
        session = current_session(request)
        return {'settings': read_settings(), 'products': read_products(False), 'csrf': session['csrf_token']}

    @app.post('/api/admin/logout')
    def logout(request: Request, response: Response):
        current_session(request, True)
        token = request.cookies.get('goodz_session')
        with connect(database) as c:
            c.execute('DELETE FROM sessions WHERE token_hash=?', (hashlib.sha256(token.encode()).hexdigest(),))
        response.delete_cookie('goodz_session', secure=os.environ.get('COOKIE_SECURE') == '1', samesite='strict')
        return {'ok': True}

    @app.put('/api/admin/settings')
    def save_settings(payload: SettingsRequest, request: Request):
        current_session(request, True)
        if not payload.values or len(payload.values) > len(DEFAULTS):
            raise HTTPException(422, 'Nenhum campo válido informado.')
        for key, value in payload.values.items():
            if key not in DEFAULTS or not isinstance(value, str):
                raise HTTPException(422, 'Campo não permitido.')
            if key in LINK_KEYS and not valid_url(value):
                raise HTTPException(422, f'URL inválida em {key}.')
            if key in IMAGE_KEYS and not image_url(value):
                raise HTTPException(422, f'Imagem inválida em {key}.')
            if key in TEXT_KEYS and len(value) > 600:
                raise HTTPException(422, 'Texto muito longo.')
        with connect(database) as c:
            for key, value in payload.values.items():
                c.execute('UPDATE settings SET value=? WHERE key=?', (value.strip(), key))
        return {'settings': read_settings()}

    @app.post('/api/admin/upload')
    async def upload(request: Request, file: UploadFile = File(...)):
        current_session(request, True)
        if file.content_type not in {'image/png','image/jpeg','image/webp'}:
            raise HTTPException(415, 'Envie PNG, JPG ou WebP.')
        raw = await file.read(MAX_UPLOAD + 1)
        if len(raw) > MAX_UPLOAD:
            raise HTTPException(413, 'Arquivo excede 8 MB.')
        try:
            img = Image.open(io.BytesIO(raw))
            if img.format not in {'PNG', 'JPEG', 'WEBP'} or img.width * img.height > 24_000_000 or min(img.size) < 2:
                raise ValueError('Formato ou dimensões inválidas.')
            img = ImageOps.exif_transpose(img)
            img.thumbnail((2200, 2200), Image.Resampling.LANCZOS)
            if img.mode not in {'RGB', 'RGBA'}:
                img = img.convert('RGBA' if 'A' in img.getbands() else 'RGB')
            out = io.BytesIO()
            img.save(out, format='WEBP', quality=84, method=6)
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            raise HTTPException(415, 'Arquivo de imagem inválido.')
        filename = uuid.uuid4().hex + '.webp'
        (uploads / filename).write_bytes(out.getvalue())
        return {'url': f'/uploads/{filename}'}

    def validate_product(p: ProductRequest):
        if not p.name.strip():
            raise HTTPException(422, 'Informe um nome válido para o produto.')
        if p.category not in CATEGORIES:
            raise HTTPException(422, 'Categoria inválida.')
        if p.image_url and not image_url(p.image_url):
            raise HTTPException(422, 'Imagem inválida.')
        return p

    @app.post('/api/admin/products', status_code=201)
    def create_product(p: ProductRequest, request: Request):
        current_session(request, True)
        validate_product(p)
        ident = uuid.uuid4().hex
        with connect(database) as c:
            c.execute('INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?)', (ident,p.category,p.name.strip(),p.description.strip(),p.price_cents,p.image_url,int(p.visible),p.sort_order,int(time.time())))
        return {'id': ident}

    @app.put('/api/admin/products/{ident}')
    def update_product(ident: str, p: ProductRequest, request: Request):
        current_session(request, True)
        validate_product(p)
        with connect(database) as c:
            changed = c.execute('UPDATE products SET category=?,name=?,description=?,price_cents=?,image_url=?,visible=?,sort_order=? WHERE id=?', (p.category,p.name.strip(),p.description.strip(),p.price_cents,p.image_url,int(p.visible),p.sort_order,ident)).rowcount
        if not changed:
            raise HTTPException(404, 'Produto não encontrado.')
        return {'ok': True}

    @app.delete('/api/admin/products/{ident}')
    def delete_product(ident: str, request: Request):
        current_session(request, True)
        with connect(database) as c:
            changed = c.execute('DELETE FROM products WHERE id=?', (ident,)).rowcount
        if not changed:
            raise HTTPException(404, 'Produto não encontrado.')
        return {'ok': True}

    @app.post('/api/admin/password')
    def change_password(p: PasswordRequest, request: Request, response: Response):
        current_session(request, True)
        with connect(database) as c:
            saved = c.execute('SELECT password_hash FROM admin_auth WHERE id=1').fetchone()
            if not saved or not verify_password(p.current_password, saved['password_hash']):
                raise HTTPException(403, 'Senha atual incorreta.')
            try:
                new_hash = password_hash(p.new_password)
            except ValueError as error:
                raise HTTPException(422, str(error))
            c.execute('UPDATE admin_auth SET password_hash=? WHERE id=1', (new_hash,))
            c.execute('DELETE FROM sessions')
        response.delete_cookie('goodz_session', secure=os.environ.get('COOKIE_SECURE') == '1', samesite='strict')
        return {'ok': True, 'relogin': True}

    return app

app = create_app()

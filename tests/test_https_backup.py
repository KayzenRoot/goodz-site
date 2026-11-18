"""Isolated HTTPS and SQLite WAL restoration qualification (no public deployment)."""
import io
import os
import shutil
import socket
import sqlite3
import ssl
import subprocess
import sys
import time
from PIL import Image
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import init_db,connect,password_hash,create_app

def test_https_login_upload_csrf_backup_restore(tmp_path):
    if not shutil.which('openssl'):
        pytest.skip('OpenSSL absent: TLS gate not qualified')
    data=tmp_path/'source'
    data.mkdir()
    dbpath=data/'goodz.sqlite3'
    init_db(dbpath)
    with connect(dbpath) as db:
        db.execute('INSERT INTO admin_auth VALUES(1,?)',(password_hash('temporary-test-password-1234'),))
    cert=tmp_path/'cert.pem'
    key=tmp_path/'key.pem'
    subprocess.run(['openssl','req','-x509','-nodes','-newkey','rsa:2048',
        '-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=localhost',
        '-addext','subjectAltName=DNS:localhost,IP:127.0.0.1',
        '-addext','basicConstraints=critical,CA:TRUE'],check=True,capture_output=True)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        port=sock.getsockname()[1]
    origin=f'https://localhost:{port}'
    proc=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app',
        '--host','127.0.0.1','--port',str(port),
        '--ssl-keyfile',str(key),'--ssl-certfile',str(cert)],
        env={**os.environ,'GOODZ_DATA_DIR':str(data),'COOKIE_SECURE':'1'},
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    uploaded=''
    try:
        with httpx.Client(base_url=origin,verify=ssl.create_default_context(cafile=str(cert)),
                          timeout=2,trust_env=False) as client:
            for _ in range(80):
                if proc.poll() is not None:
                    raise AssertionError('HTTPS server died')
                try:
                    if client.get('/health').status_code==200:break
                except httpx.TransportError:time.sleep(.15)
            else:raise AssertionError('HTTPS server did not start')
            assert client.get('/api/site').status_code==200
            login=client.post('/api/admin/login',json={'password':'temporary-test-password-1234'})
            assert login.status_code==200
            assert all(x in login.headers['set-cookie'].lower() for x in ('secure','httponly','samesite=strict'))
            token=login.json()['csrf']
            assert client.put('/api/admin/settings',json={'values':{'hero_title':'NO'}}).status_code==403
            headers={'x-csrf-token':token,'origin':origin}
            assert client.put('/api/admin/settings',headers={**headers,'origin':'https://evil.invalid'},
                              json={'values':{'hero_title':'NO'}}).status_code==403
            assert client.put('/api/admin/settings',headers=headers,
                              json={'values':{'hero_title':'GOODZ tested HTTPS'}}).status_code==200
            image=Image.new('RGB',(40,40),'gold')
            buf=io.BytesIO()
            image.save(buf,format='PNG')
            result=client.post('/api/admin/upload',headers=headers,
                files={'file':('test.png',buf.getvalue(),'image/png')})
            assert result.status_code==200,result.text
            uploaded=result.json()['url']
            assert client.get(uploaded).status_code==200
            product=client.post('/api/admin/products',headers=headers,
                json={'category':'dogueria','name':'Recovery product','image_url':uploaded,'visible':True})
            assert product.status_code==201
            assert client.post('/api/admin/logout',headers=headers).status_code==200
            assert client.get('/api/admin/state').status_code==401
            archive=tmp_path/'archive'
            archive.mkdir()
            # Controlled no-write window; sqlite3 backup includes WAL transactions.
            with sqlite3.connect(dbpath) as source,sqlite3.connect(archive/'goodz.sqlite3') as backup:
                source.backup(backup)
            shutil.copytree(data/'uploads',archive/'uploads')
    finally:
        proc.terminate()
        try:proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    restored=tmp_path/'restored'
    shutil.copytree(archive,restored)
    with sqlite3.connect(restored/'goodz.sqlite3') as db:
        assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
    with TestClient(create_app(restored)) as client:
        public=client.get('/api/site').json()
        assert public['settings']['hero_title']=='GOODZ tested HTTPS'
        assert any(p['name']=='Recovery product' for p in public['products'])
        assert client.get(uploaded).status_code==200
        assert client.get('/api/admin/state').status_code==401

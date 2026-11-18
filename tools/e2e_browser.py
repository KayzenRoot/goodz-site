"""Playwright end-to-end with Uvicorn real backend and disposable local data."""
import io,os,socket,subprocess,sys,tempfile,time
from pathlib import Path
import httpx
from PIL import Image
from playwright.sync_api import sync_playwright
from app.main import init_db,connect,password_hash

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.artifacts'

def main():
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='goodz-browser-') as folder:
        data=Path(folder)
        init_db(data/'goodz.sqlite3')
        password='browser-test-password-goodz-123'
        with connect(data/'goodz.sqlite3') as db:
            db.execute('INSERT INTO admin_auth VALUES(1,?)',(password_hash(password),))
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0))
            port=sock.getsockname()[1]
        origin=f'http://127.0.0.1:{port}'
        proc=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app',
            '--host','127.0.0.1','--port',str(port)],cwd=ROOT,
            env={**os.environ,'GOODZ_DATA_DIR':str(data),'COOKIE_SECURE':'0'},
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            for _ in range(80):
                if proc.poll() is not None:raise RuntimeError('Backend terminated')
                try:
                    if httpx.get(origin+'/health',timeout=1,trust_env=False).status_code==200:break
                except httpx.TransportError:time.sleep(.15)
            else:raise RuntimeError('Backend did not start')
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True,channel='chrome')
                try:
                    admin=browser.new_page(viewport={'width':1365,'height':875})
                    admin.goto(origin+'/admin',wait_until='networkidle')
                    assert admin.locator('#login-screen').is_visible()
                    admin.fill('#password',password)
                    admin.locator('#login-form button').click()
                    admin.locator('#dashboard').wait_for(state='visible',timeout=15000)
                    admin.locator('[data-tab="banners"]').click()
                    admin.locator('[data-setting="hero_title"]').fill('GOODZ E2E real')
                    admin.locator('#tab-banners button[type="submit"]').click()
                    admin.locator('#status').wait_for(state='visible')
                    assert 'salvas' in admin.locator('#status').inner_text().lower()
                    admin.locator('[data-tab="produtos"]').click()
                    admin.locator('#p-category').select_option('dogueria')
                    admin.locator('#p-name').fill('Hot dog E2E')
                    image=Image.new('RGB',(64,64),'gold')
                    buf=io.BytesIO()
                    image.save(buf,format='PNG')
                    admin.locator('#p-file').set_input_files(
                        {'name':'product.png','mimeType':'image/png','buffer':buf.getvalue()})
                    admin.locator('#product-save').click()
                    admin.locator('#admin-products').get_by_role(
                        'heading',name='Hot dog E2E').wait_for(timeout=15000)
                    admin.screenshot(path=str(OUT/'admin-live.png'),full_page=True)
                    for width,height,label in ((1365,875,'desktop'),(390,844,'mobile')):
                        page=browser.new_page(viewport={'width':width,'height':height})
                        page.goto(origin+'/',wait_until='networkidle')
                        assert 'GOODZ E2E real' in ' '.join(page.locator('#hero-heading').inner_text().split())
                        assert page.locator('#product-grid').get_by_text('Hot dog E2E').is_visible()
                        assert not page.evaluate(
                            'document.documentElement.scrollWidth > document.documentElement.clientWidth')
                        page.screenshot(path=str(OUT/f'site-{label}-live.png'),full_page=True)
                        page.close()
                    admin.locator('#logout').click()
                    admin.locator('#login-screen').wait_for(state='visible')
                    admin.reload(wait_until='networkidle')
                    assert admin.locator('#login-screen').is_visible()
                    print('Browser E2E PASS with real backend, upload, admin and both viewports')
                finally:browser.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

if __name__=='__main__':
    main()

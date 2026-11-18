import io
import sqlite3
from PIL import Image
from fastapi.testclient import TestClient
import pytest
from app.main import create_app, init_db, connect, password_hash

@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path)
    with TestClient(app) as c:
        yield c

def login(client, password='uma-senha-muito-forte-123'):
    return client.post('/api/admin/login', json={'password':password})

def test_public_content_and_assets(client):
    response=client.get('/')
    assert response.status_code==200
    assert 'GOODZ' in response.text
    assert client.get('/assets/logo-goodz.webp').status_code==200
    assert client.get('/health').json()['status']=='ok'
    assert client.get('/api/site').json()['products']==[]
    assert client.get('/admin').status_code==200
    assert 'no-store' in client.get('/admin').headers['cache-control']

def test_unconfigured_admin_and_auth(client, tmp_path):
    assert client.get('/api/admin/state').status_code == 401
    assert login(client).status_code == 401
    with connect(tmp_path/'goodz.sqlite3') as db:
        db.execute('INSERT INTO admin_auth VALUES(1,?)',(password_hash('uma-senha-muito-forte-123'),))
    assert login(client,'incorreta').status_code==401
    result=login(client)
    assert result.status_code == 200
    assert 'httponly' in result.headers['set-cookie'].lower()
    assert 'samesite=strict' in result.headers['set-cookie'].lower()
    token=result.json()['csrf']
    assert client.get('/api/admin/state').json()['csrf']==token
    assert client.put('/api/admin/settings',json={'values':{'hero_title':'Novo'}}).status_code==403
    assert client.put('/api/admin/settings',headers={'x-csrf-token':'errado'},json={'values':{'hero_title':'Novo'}}).status_code==403
    ok=client.put('/api/admin/settings',headers={'x-csrf-token':token},json={'values':{'hero_title':'Novo'}})
    assert ok.status_code==200
    assert client.get('/api/site').json()['settings']['hero_title']=='Novo'
    assert client.post('/api/admin/logout', headers={'x-csrf-token':token}).status_code==200
    assert client.get('/api/admin/state').status_code==401

def test_persistence_links_products_upload_and_password(client,tmp_path):
    with connect(tmp_path/'goodz.sqlite3') as db:
        db.execute('INSERT INTO admin_auth VALUES(1,?)',(password_hash('uma-senha-muito-forte-123'),))
    token=login(client).json()['csrf']; headers={'x-csrf-token':token}
    assert client.put('/api/admin/settings',json={'values':{'ifood_url':'javascript:alert(1)'}},headers=headers).status_code==422
    assert client.put('/api/admin/settings',json={'values':{'unknown':'x'}},headers=headers).status_code==422
    assert client.put('/api/admin/settings',json={'values':{'ifood_url':'https://www.ifood.com.br/'}},headers=headers).status_code==200
    assert client.post('/api/admin/upload',headers=headers,files={'file':('bad.png',b'notpng','image/png')}).status_code==415
    img=Image.new('RGB',(300,300),'gold');buf=io.BytesIO();img.save(buf,format='PNG')
    upload=client.post('/api/admin/upload',headers=headers,files={'file':('photo.png',buf.getvalue(),'image/png')})
    assert upload.status_code==200
    url=upload.json()['url'];assert url.startswith('/uploads/') and client.get(url).status_code==200
    assert client.put('/api/admin/settings',json={'values':{'logo_goodz':url}},headers=headers).status_code==200
    item={'category':'pastelaria','name':'Exemplo','description':'Descrição','price_cents':1990,'visible':True,'image_url':url}
    result=client.post('/api/admin/products',json=item,headers=headers)
    assert result.status_code==201
    ident=result.json()['id']
    assert client.get('/api/site').json()['products'][0]['price_cents']==1990
    item['visible']=False
    assert client.put('/api/admin/products/'+ident,json=item,headers=headers).status_code==200
    assert client.get('/api/site').json()['products']==[]
    assert len(client.get('/api/admin/state').json()['products'])==1
    assert client.delete('/api/admin/products/'+ident,headers=headers).status_code==200
    assert client.post('/api/admin/password',json={'current_password':'wrong','new_password':'nova-senha-segura-456'},headers=headers).status_code==403
    assert client.post('/api/admin/password',json={'current_password':'uma-senha-muito-forte-123','new_password':'nova-senha-segura-456'},headers=headers).status_code==200
    assert client.get('/api/admin/state').status_code==401
    assert login(client,'nova-senha-segura-456').status_code==200
    with connect(tmp_path/'goodz.sqlite3') as db:
        assert db.execute('SELECT value FROM settings WHERE key="logo_goodz"').fetchone()[0]==url

def test_rate_limit(client):
    for _ in range(6):
        assert login(client,'wrong').status_code==401
    assert login(client,'wrong').status_code==429

def test_upload_mime_and_product_validation(client,tmp_path):
    with connect(tmp_path/'goodz.sqlite3') as db:
        db.execute('INSERT INTO admin_auth VALUES(1,?)',(password_hash('uma-senha-muito-forte-123'),))
    h={'x-csrf-token':login(client).json()['csrf']}
    assert client.post('/api/admin/upload',headers=h,files={'file':('x.svg',b'<svg></svg>','image/svg+xml')}).status_code==415
    assert client.post('/api/admin/products',json={'category':'invalida','name':'X'},headers=h).status_code==422
    assert client.post('/api/admin/products',json={'category':'pastelaria','name':'X','image_url':'https://evil.com/a.png'},headers=h).status_code==422

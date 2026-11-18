"""Local browser preview with in-memory API mocks (not HTTP E2E)."""
from base64 import b64encode
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from app.main import DEFAULTS

ROOT=Path(__file__).resolve().parents[1]

def prepare(name):
    html=(ROOT/'static'/name).read_text()
    css=(ROOT/'static/styles'/('site.css' if name=='index.html' else 'admin.css')).read_text()
    js=(ROOT/'static/scripts'/('site.js' if name=='index.html' else 'admin.js')).read_text()
    for file in (ROOT/'static/assets').iterdir():
        raw=file.read_bytes()
        mime='image/png' if file.suffix=='.png' else ('image/jpeg' if file.suffix=='.jpg' else 'image/webp')
        html=html.replace('/assets/'+file.name,'data:'+mime+';base64,'+b64encode(raw).decode())
    html=html.replace('<link rel="stylesheet" href="/styles/'+('site' if name=='index.html' else 'admin')+'.css">','<style>'+css+'</style>')
    script_name='site' if name=='index.html' else 'admin'
    html=html.replace(f'<script src="/scripts/{script_name}.js" defer></script>',f'<script>{js}</script>')
    return html

public_stub='''window.fetch=async()=>({ok:true,status:200,json:async()=>({settings:window.goodzSettings,products:[]})});'''
admin_stub='''window.goodzAuthed=false;window.fetch=async(url,opts={})=>{let data;
if(url==='/api/admin/login'){window.goodzAuthed=true;data={csrf:'preview-token'};}
else if(url==='/api/admin/state'){if(!window.goodzAuthed)return new Response(JSON.stringify({detail:'Unauthorized'}),{status:401,headers:{'Content-Type':'application/json'}});data={settings:window.goodzSettings,products:[],csrf:'preview-token'};}
else data={ok:true,settings:window.goodzSettings};
return new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}})};'''

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for name,w,h in [('desktop',1440,900),('mobile',390,844)]:
            page=browser.new_page(viewport={'width':w,'height':h})
            html=prepare('index.html')
            html=html.replace('<script>', '<script>window.goodzSettings='+json.dumps(DEFAULTS)+';'+public_stub+'\n',1)
            page.set_content(html,wait_until='load');page.wait_for_timeout(250)
            assert page.locator('h1 em').inner_text()=='merece'
            assert not page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth')
            page.screenshot(path=str(ROOT/(name+'.png')),full_page=True)
            print(name,'site PASS')
            page.close()
            page=browser.new_page(viewport={'width':w,'height':h})
            html=prepare('admin.html')
            html=html.replace('<script>', '<script>window.goodzSettings='+json.dumps(DEFAULTS)+';'+admin_stub+'\n',1)
            page.set_content(html,wait_until='load');page.wait_for_timeout(300)
            assert page.locator('#login-screen').is_visible()
            page.screenshot(path=str(ROOT/('admin-login-'+name+'.png')),full_page=True)
            page.fill('#password','senha-de-previa');page.click('#login-form button');page.wait_for_timeout(250)
            assert page.locator('#dashboard').is_visible()
            page.click('[data-tab="banners"]')
            assert page.locator('#tab-banners').is_visible()
            page.screenshot(path=str(ROOT/('admin-dashboard-'+name+'.png')),full_page=True)
            print(name,'admin navigation PASS')
            page.close()
        browser.close()

if __name__=='__main__':main()

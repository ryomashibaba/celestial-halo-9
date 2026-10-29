"""Chromium UI test with a real ASGI/TestClient bridge; Chromium localhost blocked by sandbox.
Separately test actual uvicorn localhost HTTP with Python requests; do not overclaim browser transport.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
from fastapi.testclient import TestClient
from d29_visual_workbench import D29Workspace,create_app,D29_HTML
from d29_orthogonal_csg import fixture_glb
from d28_visual_workbench import VIEWS
from urllib.parse import urlparse
import tempfile,base64,json,requests,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='d29_browser_') as work:
    src=Path(work)/'source.glb';src.write_bytes(fixture_glb())
    client=TestClient(create_app(D29Workspace(Path(work)/'state',src)))
    def backend(source,url,body=None):
        endpoint=urlparse(url).path
        if endpoint=='/api/state':r=client.get(endpoint)
        else:r=client.post(endpoint,json=body)
        imgs={mode:{v:'data:image/png;base64,'+base64.b64encode(client.get('/api/'+prefix+'/'+v).content).decode('ascii') for v in VIEWS} for mode,prefix in [('base','baseview'),('edit','view'),('diff','diffview')]} if endpoint in ('/api/state','/api/edit','/api/undo','/api/cut') else {}
        return {'ok':r.is_success,'status':r.status_code,'body':r.json(),'images':imgs}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-gpu'])
        page=browser.new_page(viewport={'width':1520,'height':1300},device_scale_factor=1)
        errors=[];page.on('pageerror',lambda exc:errors.append(str(exc)))
        page.expose_binding('d29_backend',backend)
        old="box.querySelector('img').src='/api/'+(displayMode==='base'?'baseview':displayMode==='diff'?'diffview':'view')+'/'+box.dataset.view+'?v='+encodeURIComponent(state.revision);"
        assert old in D29_HTML
        patched=D29_HTML.replace(old, "box.querySelector('img').src=window.D29_IMAGES[displayMode][box.dataset.view];")
        bridge='''<script>
window.D29_IMAGES={};window.fetch=async function(url,options={}){
 const request=await window.d29_backend(url,options.body?JSON.parse(options.body):null);
 if(request.images&&Object.keys(request.images).length){window.D29_IMAGES=request.images;}
 return {ok:request.ok,status:request.status,json:async()=>request.body};
};</script>'''
        patched=patched.replace('<script>',bridge+'\n<script>',1)
        page.set_content(patched,wait_until='load')
        page.wait_for_function("document.querySelector('#status').textContent.includes('公共空洞 0個')",timeout=25000)
        page.wait_for_function("[...document.querySelectorAll('.viewport img')].every(x=>x.complete && x.naturalWidth>0)",timeout=25000)
        assert page.locator('.viewport').count()==6
        page.screenshot(path=str(ROOT/'D29_BROWSER_INITIAL.png'),full_page=True)
        for id,n in [('cut_entry',1),('cut_room',2),('cut_roof',3)]:
            page.locator('#'+id).click()
            page.wait_for_function("n=>document.querySelector('#status').textContent.includes('公共空洞 '+n+'個')",arg=n,timeout=25000)
            assert '拒否' not in page.locator('#message').inner_text(),page.locator('#message').inner_text()
            page.screenshot(path=str(ROOT/f'D29_BROWSER_AFTER_{n}.png'),full_page=True)
        page.locator('#mode_diff').click()
        page.screenshot(path=str(ROOT/'D29_BROWSER_DIFF.png'),full_page=True)
        page.locator('#undo').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('公共空洞 2個')",timeout=25000)
        page.screenshot(path=str(ROOT/'D29_BROWSER_UNDO.png'),full_page=True)
        assert not errors,errors
        browser.close()
    report={'chromium_UI_JS':'PASS','transport':'FastAPI TestClient shim; Chromium direct localhost blocked by sandbox',
       'real_glb_rendered_images_per_step':6,'preset_cuts_clicked':3,'undo_in_browser':True,'page_errors':errors}
    (ROOT/'D29_BROWSER_QA.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report,indent=2))

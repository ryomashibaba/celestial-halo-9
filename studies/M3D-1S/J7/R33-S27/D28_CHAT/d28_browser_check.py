"""Chromium UI test with a TestClient transport bridge (network sandbox disallows localhost)."""
from playwright.sync_api import sync_playwright
from pathlib import Path
from fastapi.testclient import TestClient
from d28_visual_workbench import Workspace,create_app,HTML,VIEWS
from urllib.parse import urlparse
import tempfile,base64,json
P=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='d28_browser_') as work:
    client=TestClient(create_app(Workspace(Path(work))))
    def backend(source,url,body=None):
        endpoint=urlparse(url).path
        if endpoint=='/api/state':r=client.get(endpoint)
        else:r=client.post(endpoint,json=body)
        # Include regenerated PNG from same saved GLB in test bridge.
        images={mode:{v:'data:image/png;base64,'+base64.b64encode(client.get('/api/'+prefix+'/'+v).content).decode('ascii') for v in VIEWS} for mode,prefix in [('base','baseview'),('edit','view'),('diff','diffview')]} if endpoint in ['/api/state','/api/edit','/api/undo'] else {}
        return {'ok':r.is_success,'status':r.status_code,'body':r.json(),'images':images}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-gpu'])
        page=browser.new_page(viewport={'width':1520,'height':1020},device_scale_factor=1)
        errors=[];page.on('pageerror',lambda exc:errors.append(str(exc)))
        page.expose_binding('d28_backend',backend)
        patched=HTML.replace("box.querySelector('img').src='/api/'+(displayMode==='base'?'baseview':displayMode==='diff'?'diffview':'view')+'/'+box.dataset.view+'?v='+encodeURIComponent(state.revision);", "box.querySelector('img').src=window.D28_IMAGES[displayMode][box.dataset.view];")
        patch_fetch='''<script>
window.D28_IMAGES={};window.fetch=async function(url,options={}){
  const req=await window.d28_backend(url,options.body?JSON.parse(options.body):null);
  if(req.images&&Object.keys(req.images).length){window.D28_IMAGES=req.images;}
  return {ok:req.ok,status:req.status,json:async()=>req.body};
};
</script>'''
        patched=patched.replace('<script>',patch_fetch+'\n<script>',1)
        page.set_content(patched,wait_until='load')
        page.wait_for_function("document.querySelector('#status').textContent.includes('編集 0回')",timeout=20000)
        page.wait_for_function("[...document.querySelectorAll('.viewport img')].every(x=>x.complete && x.naturalWidth>0)",timeout=20000)
        assert page.locator('.viewport').count()==6
        page.screenshot(path=str(P/'D28_BROWSER_BASE.png'),full_page=True)
        img=page.locator('.viewport[data-view="front"] img');box=img.bounding_box()
        page.mouse.click(box['x']+box['width']*.30,box['y']+box['height']*.53)
        page.wait_for_function("document.querySelector('#selected').textContent.includes('NEUTRAL_A')",timeout=20000)
        page.locator('#edit').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('編集 1回')",timeout=30000)
        assert '実GLBを保存' in page.locator('#message').inner_text()
        page.screenshot(path=str(P/'D28_BROWSER_EDIT.png'),full_page=True)
        page.locator('#mode_diff').click()
        page.screenshot(path=str(P/'D28_BROWSER_DIFF.png'),full_page=True)
        page.locator('#mode_base').click()
        page.screenshot(path=str(P/'D28_BROWSER_BASE_COMPARE.png'),full_page=True)
        page.locator('#mode_edit').click()
        page.locator('#undo').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('編集 0回')",timeout=30000)
        assert not errors, f'JS errors: {errors}'
        print('PASS: real Chromium UI/JS with ASGI transport bridge, 6 real 3D images, pick-edit-undo, zero page errors')
        browser.close()

"""Browser UI test: use real Chromium, but intercept transport because local HTTP is blocked by runtime policy.
UI itself is the real D33 HTML/Plotly JS. Requests are handed to actual FastAPI TestClient.
This does NOT certify native Chromium -> localhost connectivity on another machine.
"""
import json,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient
from d33_visual_editor import create_app
ROOT=Path(__file__).resolve().parent
app=create_app(ROOT); client=TestClient(app)
html=(ROOT/'D33_EDITOR.html').read_text(encoding='utf-8').replace('<script src="/vendor/plotly.min.js"></script>','')

def bridge(source,url,options=None):
    options=options or {};p=str(url); method=options.get('method','GET').upper()
    if method=='POST':
        r=client.post(p,data=options.get('body',''),headers={'content-type':'application/json'})
    else:r=client.get(p)
    return {'status':r.status_code,'body':r.text,'type':r.headers.get('content-type','application/json')}

try:
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':1500,'height':930},device_scale_factor=1)
  logs=[];page.on('pageerror',lambda exc:logs.append(str(exc)))
  page.expose_binding('py_fetch',bridge)
  page.evaluate('''window.fetch = async (url, options={}) => {
      const r=await window.py_fetch(url,options);
      return new Response(r.body,{status:r.status,headers:{'Content-Type':r.type}});
  }''')
  page.add_script_tag(content=(ROOT/'plotly.min.js').read_text(encoding='utf-8'))
  page.set_content(html,wait_until='load',timeout=25000)
  page.wait_for_function("document.querySelector('#revision').textContent.includes('Revision 0')",timeout=30000)
  page.wait_for_timeout(2000)
  page.screenshot(path=str(ROOT/'D33_BROWSER_BASE.png'),full_page=True)
  info=page.evaluate("() => ({fallback:document.querySelector('#fallback').style.display,images:document.querySelectorAll('#fallback img').length,webgl:glcap})")
  print('UI',info)
  page.locator('#object').select_option('MAIN_SHEAR')
  page.locator('#handle').select_option('3-3')
  oldx=float(page.locator('#x').input_value())
  page.locator('#x').fill(str(oldx+65))
  page.locator('#apply').click()
  page.wait_for_function("document.querySelector('#revision').textContent.includes('Revision 1')",timeout=30000)
  page.wait_for_timeout(1400)
  page.screenshot(path=str(ROOT/'D33_BROWSER_EDIT.png'),full_page=True)
  edited_status=page.locator('#status').inner_text()
  page.locator('#compare').click();page.wait_for_timeout(1300)
  page.screenshot(path=str(ROOT/'D33_BROWSER_BASE_GHOST_COMPARE.png'),full_page=True)
  ghost_count=page.evaluate("document.querySelectorAll('#fallback img').length")
  page.locator('#undo').click()
  page.wait_for_function("document.querySelector('#revision').textContent.includes('Revision 2')",timeout=30000)
  undo_status=page.locator('#status').inner_text()
  print('EDIT',edited_status[:160],'UNDO',undo_status[:140], 'ERRORS',logs[:3])
  assert info['fallback']=='block' and info['images']==6,info
  assert ghost_count==6,ghost_count
  assert 'Saved full GLB' in edited_status
  assert undo_status.startswith('Undo saved')
  assert not logs,logs
  result={'result':'PASS_WITH_TRANSPORT_SHIM_AND_VTK_FALLBACK','method':'real Chromium + actual D33 HTML/Plotly + real FastAPI TestClient; local HTTP transport intercepted due to runtime policy','webgl_supported':info['webgl'],'fallback_images':info['images'],'glb_triangles':32436,'base_revision':0,'edit_revision':1,'undo_revision':2,'fallback_images_after_toggle':ghost_count,'browser_errors':logs,'limitation':'Chromium direct localhost access is not certified'}
  (ROOT/'D33_BROWSER_TEST.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
  browser.close()
except Exception as e:
 print('BROWSER FAIL',type(e).__name__,str(e)[:1500]);traceback.print_exc()
 (ROOT/'D33_BROWSER_TEST.json').write_text(json.dumps({'result':'FAIL','error':str(e)},indent=2));raise

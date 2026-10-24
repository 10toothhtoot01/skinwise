"""Measure actual CDN Camera Kit startup against a fake Chromium camera.
No physical webcam and no paid /api/analyze call. Not proof of real device quality.
"""
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

out=Path(os.environ.get('SKINWISE_EVIDENCE_DIR','../../work/qa-actual-camera'))
out.mkdir(parents=True,exist_ok=True)
base=os.environ.get('SKINWISE_BASE_URL','http://127.0.0.1:5173')
result={'environment':'Chromium fake video device; fake permission UI; localhost','analysisCalls':0,'sdkResponses':[],'uncaughtErrors':0,'sanitizedErrors':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    context=browser.new_context(permissions=['camera'],viewport={'width':1280,'height':1000})
    page=context.new_page()
    page.add_init_script("""(() => {
      const events=[]; window.__sdkObserved={events}; let current;
      Object.defineProperty(window,'YMK',{configurable:true,get:()=>current,set:value=>{
        if (!value || typeof value!=='object') {current=value;return;}
        current=new Proxy(value,{get(target,key){
          const original=Reflect.get(target,key);
          if(key==='addEventListener' && typeof original==='function')return (name,handler)=>original.call(target,name,payload=>{
            if(['cameraFailed','unsupportedResolution','cameraOpened','closed'].includes(name))events.push({name,payload});
            handler(payload);
          });
          return typeof original==='function'?original.bind(target):original;
        }});
      }});
    })();""")
    def block_analysis(route):
        result['analysisCalls']+=1
        route.abort()
    page.route('**/api/analyze*',block_analysis)
    def error_event(error):
        result['uncaughtErrors']+=1
        # Strip URL query/fragment values; no request bodies, cookies or credentials logged.
        safe=re.sub(r'(https?://[^\s?#)]+)[?#][^\s)]*',r'\1?[redacted]',str(getattr(error,'stack',None) or error))
        result['sanitizedErrors'].append(safe[:1600])
    page.on('pageerror',error_event)
    def response_event(response):
        url=urlsplit(response.url)
        if url.hostname and ('makeupar.com' in url.hostname or 'perfectcorp.com' in url.hostname):
            result['sdkResponses'].append({'host':url.hostname,'path':url.path,'status':response.status})
    page.on('response',response_event)
    page.goto(base);page.wait_for_load_state('networkidle')
    page.get_by_role('navigation').get_by_role('button',name='Skin check',exact=True).click()
    section=page.get_by_role('region',name='Guided camera capture')
    result['beforeStart']=section.inner_text()
    page.get_by_role('button',name='Open guided camera').click()
    for _ in range(30):
        page.wait_for_timeout(1000)
        if section.get_by_role('alert').count():break
        if section.get_by_label('Current capture checks').count():
            # Observe startup + checks only. Never ask it to create a REST job.
            page.wait_for_timeout(2000)
            break
    result['afterStart']=section.inner_text()
    result['cameraUiMounted']=page.locator('#YMK-module').evaluate('(el)=>el.children.length>0')
    result['sdkPresent']=page.evaluate('Boolean(window.YMK)')
    result['sdkEvents']=page.evaluate('window.__sdkObserved.events')
    page.screenshot(path=str(out/'actual-sdk-fake-camera.png'),full_page=True)
    if page.get_by_role('button',name='Close camera').count():page.get_by_role('button',name='Close camera').click()
    context.close();browser.close()
(out/'actual-sdk-fake-camera.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))

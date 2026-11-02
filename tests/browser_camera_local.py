"""Browser camera lifecycle: real canvas-backed MediaStreams, deterministic ML adapter. No hardware/provider claim."""
import json,os,unittest
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
BASE=os.environ.get('SKINWISE_BASE_URL','http://127.0.0.1:5173').rstrip('/')
OUT=Path('../../work/qa-camera-local');OUT.mkdir(parents=True,exist_ok=True)
MOCK=r'''(() => {
 window.cameraQA={streams:[],calls:0,workers:[],frames:[],mode:'ok',model:'ok',pending:[]};
 navigator.mediaDevices.getUserMedia=async () => {
  const q=window.cameraQA;q.calls++;
  if(q.mode==='delayed')await new Promise(resolve=>q.pending.push(resolve));
  if(q.mode!=='ok'&&q.mode!=='delayed')throw new DOMException('QA camera failure',q.mode);
  const c=document.createElement('canvas');c.width=q.portrait?480:640;c.height=q.portrait?640:480;const x=c.getContext('2d');x.fillStyle='#ff0000';x.fillRect(0,0,c.width/2,c.height);x.fillStyle='#0000ff';x.fillRect(c.width/2,0,c.width/2,c.height);const s=c.captureStream(5);q.streams.push(s);return s;
 };
 navigator.mediaDevices.enumerateDevices=async()=>[{kind:'videoinput',deviceId:'front'},{kind:'videoinput',deviceId:'back'}];
 window.Worker=class {
  constructor(){this.stopped=false;window.cameraQA.workers.push(this)}
  terminate(){this.stopped=true}
  postMessage(data){const q=window.cameraQA;if(data.bitmap){q.frames.push([data.bitmap.width,data.bitmap.height]);data.bitmap.close()}
   if(q.model==='slow')return;
   setTimeout(()=>{if(this.stopped)return;if(q.model==='failure'){this.onmessage?.({data:{id:data.id,error:'model failed'}});return;}
    this.onmessage?.({data:data.bitmap?{id:data.id,faceCount:1,bounds:{x:.2,y:.2,width:.6,height:.6},warnings:[],elapsedMs:7}:{id:data.id,ready:true}})
   },10)
  }
 };
})();'''
class CameraLocal(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch()
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.p.stop()
 def setUp(self):
  self.context=self.browser.new_context(viewport={'width':390,'height':844});self.context.add_init_script(MOCK);self.page=self.context.new_page();self.errors=[];self.paid=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)));self.page.route('**/api/status',lambda r:r.fulfill(json={'configured':True}));self.page.route('**/api/makeup*',lambda r:(self.paid.append(r.request.method),r.abort()));self.page.goto(BASE+'/planner');self.page.wait_for_load_state('networkidle')
 def tearDown(self):
  self.page.screenshot(path=str(OUT/(self._testMethodName+'.png')),full_page=True);(OUT/(self._testMethodName+'.json')).write_text(json.dumps({'errors':self.errors,'providerAttempts':self.paid},indent=2));self.context.close();self.assertEqual([],self.errors);self.assertEqual([],self.paid)
 def open(self):self.page.get_by_role('button',name='Open browser camera',exact=True).click();expect(self.page.get_by_role('button',name='Capture photo',exact=True)).to_be_enabled()
 def stopped(self):return self.page.evaluate('cameraQA.streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))')
 def test_permission_errors_and_insecure_fallback(self):
  for kind,text in [('NotAllowedError','Camera permission was not granted'),('NotFoundError','No camera was found'),('NotReadableError','The camera could not start'),('OverconstrainedError','cannot provide the requested view')]:
   self.page.evaluate('(mode)=>cameraQA.mode=mode',kind);self.page.get_by_role('button',name='Open browser camera',exact=True).click();expect(self.page.get_by_role('status').filter(has_text=text)).to_be_visible();self.assertTrue(self.stopped())
  self.page.evaluate('Object.defineProperty(window,"isSecureContext",{value:false})');self.page.get_by_role('button',name='Open browser camera',exact=True).click();expect(self.page.get_by_role('status').filter(has_text='needs HTTPS or localhost')).to_be_visible();self.assertEqual(4,self.page.evaluate('cameraQA.calls'))
 def test_capture_review_mirror_retaking_and_pipeline(self):
  self.assertEqual(0,self.page.evaluate('cameraQA.calls'));self.open();expect(self.page.get_by_text('One face detected',exact=True)).to_be_visible();self.assertEqual('matrix(-1, 0, 0, 1, 0, 0)',self.page.locator('video').evaluate('e=>getComputedStyle(e).transform'))
  self.page.get_by_role('button',name='Capture photo',exact=True).click();review=self.page.get_by_alt_text('Original unmirrored camera capture for review');expect(review).to_be_visible();self.assertTrue(self.stopped());self.assertTrue(self.page.evaluate('cameraQA.workers.every(w=>w.stopped)'))
  pixels=review.evaluate('async e=>{await e.decode();const c=document.createElement("canvas");c.width=e.naturalWidth;c.height=e.naturalHeight;const x=c.getContext("2d");x.drawImage(e,0,0);return {width:c.width,height:c.height,left:[...x.getImageData(50,50,1,1).data],right:[...x.getImageData(c.width-50,50,1,1).data]}}');self.assertEqual(640,pixels['width']);self.assertEqual(480,pixels['height']);self.assertEqual([255,0,0,255],pixels['left']);self.assertEqual([0,0,255,255],pixels['right'])
  self.page.get_by_role('button',name='Retake photo',exact=True).click();expect(self.page.get_by_role('button',name='Capture photo',exact=True)).to_be_enabled();self.page.get_by_role('button',name='Capture photo',exact=True).click();self.page.get_by_role('button',name='Use this capture',exact=True).click();expect(self.page.get_by_alt_text('Prepared original portrait',exact=True)).to_be_visible();self.assertFalse(self.page.get_by_label('I have permission',exact=False).is_checked());self.assertTrue(self.stopped());self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
 def test_switch_cancel_route_and_late_permission_cleanup(self):
  self.open();self.page.get_by_role('button',name='Switch camera',exact=True).click();expect(self.page.get_by_role('button',name='Capture photo',exact=True)).to_be_enabled();self.assertEqual('none',self.page.locator('video').evaluate('e=>getComputedStyle(e).transform'));self.assertTrue(self.page.evaluate('cameraQA.streams[0].getTracks().every(t=>t.readyState==="ended")'));self.page.get_by_role('button',name='Cancel camera',exact=True).click();self.assertTrue(self.stopped())
  self.page.evaluate('cameraQA.mode="delayed"');self.page.get_by_role('button',name='Open browser camera',exact=True).click();expect(self.page.get_by_text('Waiting for camera permission… You can close this panel to cancel.',exact=True)).to_be_visible();self.page.get_by_role('button',name='Cancel camera',exact=True).click();self.page.evaluate('cameraQA.pending[0]()');self.page.wait_for_function('cameraQA.streams.length===3&&cameraQA.streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))');expect(self.page.get_by_role('button',name='Capture photo',exact=True)).to_have_count(0)
  self.page.evaluate('cameraQA.mode="ok"');self.open();self.page.evaluate('window.dispatchEvent(new PageTransitionEvent("pagehide"))');self.assertTrue(self.stopped());self.assertTrue(self.page.evaluate('cameraQA.workers.every(w=>w.stopped)'))
 def test_actual_navigation_stops_tracks_before_leaving(self):
  self.open();self.page.evaluate('window.addEventListener("pagehide",()=>sessionStorage.setItem("camera-qa-left",JSON.stringify({stopped:cameraQA.streams.every(s=>s.getTracks().every(t=>t.readyState==="ended")),workersStopped:cameraQA.workers.every(w=>w.stopped)})))');self.page.get_by_role('link',name='Skin journal',exact=True).click();expect(self.page).to_have_url(BASE+'/journal');self.assertEqual({'stopped':True,'workersStopped':True},self.page.evaluate('JSON.parse(sessionStorage.getItem("camera-qa-left"))'))
 def test_model_failure_manual_capture_and_portrait_dimensions(self):
  self.page.evaluate('cameraQA.model="failure";cameraQA.portrait=true');self.open();expect(self.page.get_by_role('status').filter(has_text='Local face guidance is unavailable')).to_be_visible();self.page.get_by_role('button',name='Capture photo',exact=True).click();review=self.page.get_by_alt_text('Original unmirrored camera capture for review');expect(review).to_be_visible();self.assertEqual([480,640],review.evaluate('e=>[e.naturalWidth,e.naturalHeight]'));self.page.get_by_role('button',name='Cancel camera',exact=True).click();expect(self.page.get_by_alt_text('Prepared original portrait',exact=True)).to_have_count(0);self.assertTrue(self.stopped())
 def test_model_timeout_preserves_manual_capture_and_close_cancels_loading(self):
  self.page.evaluate('cameraQA.model="slow";const native=setTimeout;window.setTimeout=(fn,ms,...args)=>native(fn,ms===20000?40:ms,...args)');self.open();expect(self.page.get_by_role('status').filter(has_text='Local face guidance is unavailable')).to_be_visible();expect(self.page.get_by_role('button',name='Capture photo',exact=True)).to_be_enabled();self.assertTrue(self.page.evaluate('cameraQA.workers.every(w=>w.stopped)'));self.page.get_by_role('button',name='Cancel camera',exact=True).click();self.assertTrue(self.stopped())
  self.page.evaluate('cameraQA.model="slow"');self.open();self.page.get_by_role('button',name='Cancel camera',exact=True).click();self.assertTrue(self.stopped());self.assertTrue(self.page.evaluate('cameraQA.workers.every(w=>w.stopped)'))
 def test_hidden_tab_pauses_and_cancels_model(self):
  self.open();self.page.wait_for_function('cameraQA.frames.length>0');self.page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,value:true})');expect(self.page.get_by_role('status').filter(has_text='Local checks paused')).to_be_visible();count=self.page.evaluate('cameraQA.frames.length');self.page.wait_for_timeout(1500);self.assertEqual(count,self.page.evaluate('cameraQA.frames.length'));self.page.evaluate('Object.defineProperty(document,"hidden",{configurable:true,value:false})');self.page.wait_for_function('(n)=>cameraQA.frames.length>n',arg=count);self.page.get_by_role('button',name='Cancel camera',exact=True).click();self.assertTrue(self.stopped());self.assertTrue(self.page.evaluate('cameraQA.workers.every(w=>w.stopped)'))
if __name__=='__main__':unittest.main(verbosity=2)

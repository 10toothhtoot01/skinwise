"""Opt-in actual pinned ML proof using an explicitly synthetic adult image; no physical-camera claim."""
import base64,json,os,unittest
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
BASE=os.environ.get('SKINWISE_BASE_URL','http://127.0.0.1:5173').rstrip('/')
FIXTURE=Path(os.environ.get('SKINWISE_SYNTHETIC_PORTRAIT','../../work/fixtures/synthetic-adult-makeup-qa.jpg'))
OUT=Path('../../work/qa-camera-local');OUT.mkdir(parents=True,exist_ok=True)
class ActualCameraModel(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not FIXTURE.exists():raise unittest.SkipTest('Provide SKINWISE_SYNTHETIC_PORTRAIT for actual model fixture proof')
  cls.uri='data:image/jpeg;base64,'+base64.b64encode(FIXTURE.read_bytes()).decode();cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch()
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.p.stop()
 def test_actual_model_in_camera_flow_and_lossless_review(self):
  context=self.browser.new_context(viewport={'width':390,'height':844});context.add_init_script('''window.cameraStreams=[];navigator.mediaDevices.getUserMedia=async()=>{const image=await createImageBitmap(await (await fetch('''+json.dumps(self.uri)+''')).blob());const canvas=document.createElement('canvas');canvas.width=1024;canvas.height=1024;canvas.getContext('2d').drawImage(image,0,0,1024,1024);image.close();const stream=canvas.captureStream(5);window.cameraStreams.push(stream);return stream;};''')
  page=context.new_page();errors=[];paid=[];assets=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:assets.append(r.url) if '/camera/' in r.url else None);page.route('**/api/makeup*',lambda r:(paid.append(r.request.method),r.abort()));page.goto(BASE+'/planner');page.wait_for_load_state('networkidle');self.assertEqual([],assets);page.get_by_role('button',name='Open browser camera',exact=True).click();expect(page.get_by_text('One face detected',exact=True)).to_be_visible(timeout=25000);page.screenshot(path=str(OUT/'actual-model-camera-390.png'),full_page=True);page.get_by_role('button',name='Capture photo',exact=True).click();image=page.get_by_alt_text('Original unmirrored camera capture for review');expect(image).to_be_visible();self.assertEqual([1024,1024],image.evaluate('e=>[e.naturalWidth,e.naturalHeight]'));self.assertTrue(page.evaluate('cameraStreams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))'));page.get_by_role('button',name='Use this capture',exact=True).click();expect(page.get_by_alt_text('Prepared original portrait',exact=True)).to_be_visible();self.assertEqual([],errors);self.assertEqual([],paid)
  (OUT/'actual-model-camera-safe.json').write_text(json.dumps({'environment':'Linux headless Chromium; synthetic adult fixture supplied by canvas MediaStream; actual local model worker; no physical camera','assets':assets,'errors':errors,'paidProviderAttempts':paid,'captureDimensions':[1024,1024]},indent=2));context.close()
if __name__=='__main__':unittest.main(verbosity=2)

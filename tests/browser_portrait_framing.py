"""Faithful original crop/rotation regressions; synthetic chart, mocked provider only."""
import io,json,os,re,unittest
from pathlib import Path
from PIL import Image
from playwright.sync_api import expect
import browser_planner as b
E=Path('../../work/qa-framing');E.mkdir(parents=True,exist_ok=True)
class Framing(unittest.TestCase):
 setUpClass=classmethod(b.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(b.PlannerAcceptance.tearDownClass.__func__)
 setUp=b.PlannerAcceptance.setUp
 add=b.PlannerAcceptance.add
 stored=b.PlannerAcceptance.stored
 render=b.PlannerAcceptance.render
 def tearDown(self):
  self.page.screenshot(path=str(E/(self._testMethodName+'.png')),full_page=True)
  (E/(self._testMethodName+'.json')).write_text(json.dumps({'errors':self.errors,'mockCalls':self.calls,'paidCalls':0},indent=2));self.context.close()
 def chart(self,w=768,h=1024):
  im=Image.new('RGB',(w,h),'red');im.paste('blue',(w//2,0,w,h));buf=io.BytesIO();im.save(buf,format='PNG')
  self.page.get_by_label('Portrait for visual rehearsal',exact=True).set_input_files({'name':'color-chart.png','mimeType':'image/png','buffer':buf.getvalue()})
  expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_be_visible()
  self.page.get_by_role('button',name='Adjust framing before preview',exact=True).click();expect(self.page.get_by_role('button',name='Use this framing',exact=True)).to_be_enabled()
 def test_rotate_and_restore_start_from_original_without_color_edit(self):
  self.add();self.chart();before=self.stored()['sourceHash'];self.page.get_by_label(re.compile('I have permission')).check()
  self.page.get_by_role('button',name='Rotate 90°',exact=True).click();self.page.get_by_role('button',name='Use this framing',exact=True).click()
  expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_contain_text('1024 × 768 JPEG');expect(self.page.get_by_label(re.compile('I have permission'))).not_to_be_checked()
  image=self.page.get_by_role('img',name='Prepared original portrait',exact=True)
  result=image.evaluate('''async e=>{await e.decode();const c=document.createElement('canvas');c.width=e.naturalWidth;c.height=e.naturalHeight;const ctx=c.getContext('2d');ctx.drawImage(e,0,0);return [Array.from(ctx.getImageData(c.width/2,c.height/4,1,1).data),Array.from(ctx.getImageData(c.width/2,c.height*3/4,1,1).data)];}''')
  self.assertGreater(result[0][0],240);self.assertLess(result[0][2],10);self.assertGreater(result[1][2],240);self.assertLess(result[1][0],10)
  self.page.get_by_role('button',name='Use full original',exact=True).click();expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_contain_text('768 × 1024 JPEG');self.assertEqual(before,self.stored()['sourceHash']);self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_crop_preserves_detail_and_rejects_enlargement(self):
  self.add();self.chart(1600,2000);before=self.stored()['sourceHash']
  self.page.get_by_label('Framing zoom',exact=True).fill('2');self.page.get_by_role('button',name='Use this framing',exact=True).click();expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_contain_text('800 × 1000 JPEG');self.assertNotEqual(before,self.stored()['sourceHash'])
  self.page.get_by_role('button',name='Use full original',exact=True).click();expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_contain_text('819 × 1024 JPEG');self.assertEqual(before,self.stored()['sourceHash'])
  self.page.get_by_role('button',name='Close framing',exact=True).click();self.chart();self.page.get_by_label('Framing zoom',exact=True).fill('3');expect(self.page.get_by_role('button',name='Use this framing',exact=True)).to_be_disabled();expect(self.page.get_by_text('Too few original pixels remain. Zoom out or retake closer.',exact=True)).to_be_visible();self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_large_phone_sized_original_avoids_lossless_intermediate(self):
  self.add();width,height=1800,2400;original=Image.frombytes('RGB',(width,height),os.urandom(width*height*3));buf=io.BytesIO();original.save(buf,format='JPEG',quality=85);self.assertLess(len(buf.getvalue()),8*1024*1024)
  self.page.get_by_label('Portrait for visual rehearsal',exact=True).set_input_files({'name':'large-original.jpg','mimeType':'image/jpeg','buffer':buf.getvalue()});expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_be_visible();before=self.stored()['sourceHash']
  self.page.get_by_role('button',name='Adjust framing before preview',exact=True).click();expect(self.page.get_by_role('button',name='Use this framing',exact=True)).to_be_enabled();self.page.get_by_label('Framing zoom',exact=True).fill('1.1');self.page.get_by_role('button',name='Use this framing',exact=True).click();expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_be_visible();expect(self.page.get_by_role('button',name='Use this framing',exact=True)).to_be_enabled();self.assertNotEqual(before,self.stored()['sourceHash']);self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_lossless_png_option_preserves_canvas_pixels_and_original_recovery(self):
  self.add();self.chart();before=self.stored()['sourceHash'];self.page.get_by_label('Use lossless PNG for this framing',exact=True).check();self.page.get_by_role('button',name='Use this framing',exact=True).click();expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_contain_text('768 × 1024 PNG')
  image=self.page.get_by_role('img',name='Prepared original portrait',exact=True)
  result=image.evaluate("""async e=>{const b=await(await fetch(e.src)).arrayBuffer();await e.decode();const c=document.createElement('canvas');c.width=e.naturalWidth;c.height=e.naturalHeight;const x=c.getContext('2d');x.drawImage(e,0,0);return {magic:Array.from(new Uint8Array(b).slice(0,8)),pixel:Array.from(x.getImageData(c.width/4,c.height/2,1,1).data)};}""")
  self.assertEqual([137,80,78,71,13,10,26,10],result['magic']);self.assertEqual([255,0,0,255],result['pixel']);self.assertNotEqual(before,self.stored()['sourceHash']);self.page.get_by_role('button',name='Use full original',exact=True).click();expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_contain_text('768 × 1024 JPEG');self.assertEqual(before,self.stored()['sourceHash']);self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_exif_orientation_is_applied_once_before_framing(self):
  self.add();im=Image.new('RGB',(1024,768),'red');im.paste('blue',(512,0,1024,768));exif=Image.Exif();exif[274]=6;buf=io.BytesIO();im.save(buf,format='JPEG',quality=98,exif=exif)
  self.page.get_by_label('Portrait for visual rehearsal',exact=True).set_input_files({'name':'portrait-rotation.jpg','mimeType':'image/jpeg','buffer':buf.getvalue()});expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_contain_text('768 × 1024 JPEG')
  image=self.page.get_by_role('img',name='Prepared original portrait',exact=True)
  pixels=image.evaluate("""async e=>{await e.decode();const c=document.createElement('canvas');c.width=e.naturalWidth;c.height=e.naturalHeight;const x=c.getContext('2d');x.drawImage(e,0,0);return [Array.from(x.getImageData(c.width/2,c.height/4,1,1).data),Array.from(x.getImageData(c.width/2,c.height*3/4,1,1).data)];}""")
  self.assertGreater(pixels[0][0],230);self.assertLess(pixels[0][2],20);self.assertGreater(pixels[1][2],230);self.assertLess(pixels[1][0],20)
  self.page.get_by_role('button',name='Adjust framing before preview',exact=True).click();expect(self.page.get_by_role('button',name='Use this framing',exact=True)).to_be_enabled();self.page.get_by_role('button',name='Rotate 90°',exact=True).click();self.page.get_by_role('button',name='Use this framing',exact=True).click();expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_contain_text('1024 × 768 JPEG');self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_local_suggestion_requires_explicit_application_and_cancels_cleanly(self):
  self.add();self.chart(1600,2000);before=self.stored()['sourceHash'];self.page.evaluate("""()=>{window.Worker=class{postMessage(data){data.bitmap?.close();setTimeout(()=>this.onmessage?.({data:{faceCount:1,bounds:{x:.4,y:.4,width:.2,height:.2},warnings:['Face may be small.']}}),20)}terminate(){this.onmessage=null}}}""")
  self.page.get_by_role('button',name='Check photo locally',exact=True).click();suggest=self.page.get_by_role('button',name='Preview suggested framing',exact=True);expect(suggest).to_be_visible();self.assertEqual(before,self.stored()['sourceHash']);self.assertEqual([],self.calls)
  suggest.click();self.assertGreater(float(self.page.get_by_label('Framing zoom',exact=True).input_value()),1);self.assertEqual(before,self.stored()['sourceHash']);self.page.get_by_role('button',name='Use this framing',exact=True).click();self.page.wait_for_function("([key,old])=>JSON.parse(sessionStorage.getItem(key)).sourceHash!==old",arg=[b.KEY,before]);self.assertEqual([],self.calls)
  self.page.evaluate("""()=>{window.Worker=class{postMessage(data){data.bitmap?.close()}terminate(){}}}""");self.page.get_by_role('button',name='Check photo locally',exact=True).click();self.page.get_by_role('button',name='Close framing',exact=True).click();self.page.get_by_role('button',name='Adjust framing before preview',exact=True).click();expect(self.page.get_by_role('button',name='Check photo locally',exact=True)).to_be_enabled();self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_suggested_crop_does_not_propose_too_few_pixels(self):
  self.add();self.chart();self.page.evaluate("""()=>{window.Worker=class{postMessage(data){data.bitmap?.close();setTimeout(()=>this.onmessage?.({data:{faceCount:1,bounds:{x:.4,y:.4,width:.2,height:.2},warnings:[]}}),20)}terminate(){this.onmessage=null}}}""")
  self.page.get_by_role('button',name='Check photo locally',exact=True).click();self.page.get_by_role('button',name='Preview suggested framing',exact=True).click();expect(self.page.get_by_role('button',name='Use this framing',exact=True)).to_be_enabled();self.assertLessEqual(float(self.page.get_by_label('Framing zoom',exact=True).input_value()),1.6);self.assertEqual([],self.calls)
 def test_real_local_model_check_is_private_and_advisory(self):
  self.add();fixture=Path('../../work/fixtures/synthetic-adult-makeup-qa.jpg');self.page.get_by_label('Portrait for visual rehearsal',exact=True).set_input_files(str(fixture));expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_be_visible()
  self.page.get_by_role('button',name='Adjust framing before preview',exact=True).click();button=self.page.get_by_role('button',name='Check photo locally',exact=True);expect(button).to_be_enabled();button.click();expect(button).to_be_enabled(timeout=30000)
  status=self.page.locator('.framing-advice');expect(status).to_be_visible();expect(status).to_contain_text('Uncalibrated hints can miss problems');self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_cancel_crop_receipt_replacement_preserves_current_preview(self):
  self.add();self.chart();self.page.get_by_label(re.compile('I have permission')).check();self.render();before=self.stored()
  self.page.get_by_role('button',name='Rotate 90°',exact=True).click();self.page.once('dialog',lambda d:d.dismiss());self.page.get_by_role('button',name='Use this framing',exact=True).click()
  expect(self.page.get_by_role('button',name='Use this framing',exact=True)).to_be_enabled();self.assertEqual(before,self.stored());self.assertEqual(['POST','GET'],self.calls);self.assertEqual([],self.errors)
if __name__=='__main__':unittest.main(verbosity=2)

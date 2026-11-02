"""Faithful journal preprocessing, mocked provider only, real browser decoding."""
import io,json,unittest
from PIL import Image
from playwright.sync_api import expect
import browser_acceptance as base

def picture(w,h,kind='PNG',orientation=None):
 stream=io.BytesIO();image=Image.new('RGB',(w,h),(128,155,130));
 if orientation:
  exif=Image.Exif();exif[274]=orientation;image.save(stream,kind,exif=exif)
 else:image.save(stream,kind)
 return stream.getvalue()
class SkinPreparation(unittest.TestCase):
 setUpClass=classmethod(base.Acceptance.setUpClass.__func__)
 tearDownClass=classmethod(base.Acceptance.tearDownClass.__func__)
 setUp=base.Acceptance.setUp
 tearDown=base.Acceptance.tearDown
 open=base.Acceptance.open
 click_nav=base.Acceptance.click_nav
 assert_clean=base.Acceptance.assert_clean
 def capture(self):
  self.page.route('**/api/status',lambda r:r.fulfill(json={'configured':True}));self.open();self.click_nav('Skin check')
 def upload(self,data,mime='image/png',name='original.png'):
  self.page.get_by_label('Choose a skin photo',exact=True).set_input_files({'name':name,'mimeType':mime,'buffer':data})
 def prepared(self):
  return self.page.get_by_alt_text('Your selected photo, shown only in this session').evaluate('async e=>{const blob=await(await fetch(e.src)).blob();const bitmap=await createImageBitmap(blob);return {width:bitmap.width,height:bitmap.height,type:blob.type,size:blob.size}}')
 def test_large_phone_portrait_landscape_and_exact_original_preserved(self):
  self.capture();original=picture(3000,4000);self.upload(original);expect(self.page.locator('.photo-preflight')).to_contain_text('3000 × 4000');expect(self.page.locator('.skin-preparation-note')).to_contain_text('Original photo pixels and encoding retained');self.assertEqual(len(original),self.prepared()['size'])
  self.upload(picture(4000,6000));expect(self.page.locator('.photo-preflight')).to_contain_text('2731 × 4096');expect(self.page.locator('.skin-preparation-note')).to_contain_text('4000 × 6000 original');self.assertEqual({'width':2731,'height':4096}, {k:v for k,v in self.prepared().items() if k in ('width','height')});self.assertEqual('image/png',self.prepared()['type'])
  self.upload(picture(6000,4000));expect(self.page.locator('.photo-preflight')).to_contain_text('4096 × 2731');self.assertEqual([],self.analysis_requests);self.assert_clean()
 def test_wide_photo_explicit_crop_repairs_without_enlargement(self):
  self.capture();self.upload(picture(6000,600));expect(self.page.locator('.notice[role=status]')).to_contain_text('needs framing');expect(self.page.get_by_role('button',name='Analyse my skin',exact=True)).to_be_disabled();self.page.get_by_role('button',name='Frame original photo',exact=True).click();expect(self.page.get_by_role('button',name='Use this skin-photo framing',exact=True)).to_be_enabled();self.page.get_by_role('button',name='Use this skin-photo framing',exact=True).click();expect(self.page.locator('.photo-preflight')).to_contain_text('600 × 600');expect(self.page.locator('.skin-preparation-note')).to_contain_text('Your chosen crop');self.assertEqual(600,self.prepared()['width']);self.page.get_by_role('button',name='Restore full original',exact=True).click();expect(self.page.locator('.notice[role=status]')).to_contain_text('needs framing');expect(self.page.get_by_role('button',name='Analyse my skin',exact=True)).to_be_disabled();self.assertEqual([],self.analysis_requests);self.assert_clean()
 def test_decodable_formats_empty_mime_exif_and_specific_heic_error(self):
  self.capture();self.upload(picture(960,1280,'WEBP'),'image/webp','phone.webp');expect(self.page.locator('.photo-preflight')).to_contain_text('960 × 1280');self.assertEqual('image/png',self.prepared()['type']);self.upload(picture(640,960),'','unnamed.png');expect(self.page.locator('.photo-preflight')).to_contain_text('640 × 960');self.assertEqual('image/png',self.prepared()['type'])
  self.upload(picture(640,960,'JPEG',orientation=6),'image/jpeg','rotated.jpg');expect(self.page.locator('.photo-preflight')).to_contain_text('960 × 640');expect(self.page.locator('.skin-preparation-note')).to_contain_text('Camera orientation normalized');self.assertEqual([960,640],[self.prepared()['width'],self.prepared()['height']]);self.upload(b'not-a-real-heic','image/heic','phone.heic');expect(self.page.locator('.notice[role=status]')).to_contain_text('save or export it as JPEG');expect(self.page.get_by_role('button',name='Analyse my skin',exact=True)).to_be_disabled();self.assertEqual([],self.analysis_requests);self.assert_clean()
 def test_undersize_large_file_and_preparation_resets_consent(self):
  self.capture();self.upload(picture(480,640));expect(self.page.locator('.photo-preflight')).to_be_visible();self.page.locator('.consent-row input').check();self.upload(picture(6000,4000));expect(self.page.locator('.photo-preflight')).to_contain_text('4096 × 2731');self.assertFalse(self.page.locator('.consent-row input').is_checked());self.upload(picture(479,960));expect(self.page.locator('.notice[role=status]')).to_contain_text('480-pixel minimum');expect(self.page.get_by_role('button',name='Analyse my skin',exact=True)).to_be_disabled();self.upload(picture(960,960)+b'\0'*(25*1024*1024));expect(self.page.locator('.notice[role=status]')).to_contain_text('over 25 MB');self.assertEqual([],self.analysis_requests);self.assert_clean()
 def test_latest_selection_and_remove_invalidate_late_preparation(self):
  self.capture();self.page.evaluate('() => {window.skinHeld=[];const native=HTMLCanvasElement.prototype.toBlob;HTMLCanvasElement.prototype.toBlob=function(callback,...args){return native.call(this,blob=>{if(this.width===4096)skinHeld.push(()=>callback(blob));else callback(blob)},...args)};}');self.upload(picture(6000,4000));self.page.wait_for_function('skinHeld.length===1');self.upload(picture(640,960));expect(self.page.locator('.photo-preflight')).to_contain_text('640 × 960');self.page.evaluate('skinHeld.shift()()');expect(self.page.locator('.photo-preflight')).to_contain_text('640 × 960');self.upload(picture(6000,4000));self.page.wait_for_function('skinHeld.length===1');self.page.get_by_role('button',name='Remove selected photo',exact=True).click();self.page.evaluate('skinHeld.shift()()');expect(self.page.locator('.photo-preflight')).to_have_count(0);expect(self.page.get_by_role('button',name='Frame original photo',exact=True)).to_have_count(0);expect(self.page.get_by_role('button',name='Analyse my skin',exact=True)).to_be_disabled();self.assertEqual([],self.analysis_requests);self.assert_clean()
 def test_portrait_crop_rounding_stays_inside_original(self):
  self.capture();self.upload(picture(800,482));expect(self.page.locator('.photo-preflight')).to_contain_text('800 × 482');self.page.get_by_role('button',name='Frame original photo',exact=True).click();self.page.get_by_role('combobox',name='Crop shape',exact=True).select_option('0.75');expect(self.page.locator('.skin-framing-body [role=status]')).to_contain_text('362 × 482');expect(self.page.get_by_role('button',name='Use this skin-photo framing',exact=True)).to_be_disabled();self.page.get_by_role('combobox',name='Crop shape',exact=True).select_option('1');self.page.get_by_role('button',name='Use this skin-photo framing',exact=True).click();expect(self.page.locator('.photo-preflight')).to_contain_text('482 × 482');self.assertEqual([],self.analysis_requests);self.assert_clean()
 def test_mobile_framing_controls_fit_and_apply(self):
  self.page.set_viewport_size({'width':390,'height':844});self.capture();self.upload(picture(1600,2200));expect(self.page.locator('.photo-preflight')).to_contain_text('1600 × 2200');self.page.get_by_role('button',name='Frame original photo',exact=True).click();self.page.get_by_role('combobox',name='Crop shape',exact=True).select_option('0.75');self.page.get_by_role('button',name='Use this skin-photo framing',exact=True).click();expect(self.page.locator('.photo-preflight')).to_contain_text('1600 × 2133');self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390);self.assertEqual([],self.analysis_requests);self.assert_clean()
if __name__=='__main__':unittest.main(verbosity=2)

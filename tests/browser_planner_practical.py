"""Practical flow regression; mocked API, no paid calls."""
import json,re,unittest
from pathlib import Path
from playwright.sync_api import expect
import browser_planner as b
from browser_capture import png
E=Path('../../work/qa-practical');E.mkdir(parents=True,exist_ok=True)
class Practical(unittest.TestCase):
 setUpClass=classmethod(b.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(b.PlannerAcceptance.tearDownClass.__func__)
 setUp=b.PlannerAcceptance.setUp
 stored=b.PlannerAcceptance.stored
 add=b.PlannerAcceptance.add
 photo=b.PlannerAcceptance.photo
 def tearDown(self):
  self.page.screenshot(path=str(E/(self._testMethodName+'.png')),full_page=True)
  (E/(self._testMethodName+'.json')).write_text(json.dumps({'uncaughtErrors':self.errors,'mockApiMethods':self.calls,'paidProviderCalls':0},indent=2));self.context.close()
 def pair(self):
  self.add('Owned rose lip','lip_color',2);self.add('Owned cheek','blush',3);self.add('Unselected eye','eye_shadow',6)
  self.page.get_by_label('Minutes available',exact=True).fill('7')
  self.page.get_by_text('Browse all 4 feasible combinations',exact=True).click()
  self.page.locator('.planner-catalog li').filter(has_text='Owned rose lip').filter(has_text='Owned cheek').get_by_role('button',name='Choose without preview',exact=True).click()
  return self.page.get_by_role('article',name='Chosen plan to keep')
 def test_exact_plan_mobile_text_print(self):
  self.page.set_viewport_size({'width':390,'height':844});card=self.pair()
  expect(card).to_contain_text('5 estimated min / 7 available · 2 min remaining');expect(card).to_contain_text('2 products / 2 maximum');expect(card).not_to_contain_text('Unselected eye')
  with self.page.expect_download() as dl:card.get_by_role('button',name='Save plan as text').click()
  text=Path(dl.value.path()).read_text();self.assertIn('Total: 5 estimated min / 7 available; 2 min remaining',text)
  for value in ['Owned rose lip','Owned cheek']:self.assertIn(value,text)
  for value in ['Unselected eye',b.TOKEN,b.AWS,'taskId','sourceHash','data:image']:self.assertNotIn(value,text)
  (E/'chosen-plan.txt').write_text(text);self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390);card.screenshot(path=str(E/'chosen-plan-mobile.png'))
  self.page.evaluate('()=>{window.__printed=0;window.print=()=>{window.__printed++}}');card.get_by_role('button',name='Print plan').click();self.assertEqual(1,self.page.evaluate('window.__printed'))
  self.page.emulate_media(media='print');expect(self.page.locator('.planner-inputs')).to_be_hidden();expect(card.get_by_role('button',name='Print plan')).to_be_hidden();expect(card).to_be_visible();self.page.pdf(path=str(E/'chosen-plan-print.pdf'),format='A4',print_background=True);self.page.screenshot(path=str(E/'chosen-plan-print.png'),full_page=True)
  self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_no_selection_no_makeup_stale_choice(self):
  card=self.page.get_by_role('article',name='Chosen plan to keep');expect(card).to_have_count(0)
  self.page.get_by_role('button',name='Choose no added makeup',exact=True).click();expect(card).to_contain_text('explicit opt-out');expect(card.locator('li')).to_have_count(0)
  self.page.get_by_label('What are you getting ready for?',exact=True).fill('Different occasion');expect(card).to_have_count(0)
  self.pair();expect(card).to_have_count(1);self.page.get_by_label('Minutes available',exact=True).fill('4');expect(card).to_have_count(0);self.assertIsNone(self.stored()['selected']);self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_metadata_edit_receipt_reuse_color_guard(self):
  self.add('Owned rose lip');self.photo();self.page.get_by_label(re.compile('I have permission')).check();self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).click();expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=15000);self.page.get_by_role('button',name='Choose this plan',exact=True).click()
  before=self.stored()['tasks'];pid=self.stored()['products'][0]['id'];self.page.get_by_role('button',name='Edit Owned rose lip',exact=True).click();self.page.get_by_label('Product name',exact=True).fill('Corrected owned lip');self.page.get_by_label('Your minutes',exact=True).fill('2');self.page.get_by_role('button',name='Save product changes',exact=True).click()
  self.assertEqual(before,self.stored()['tasks']);self.assertEqual(pid,self.stored()['products'][0]['id']);self.assertIsNone(self.stored()['selected']);self.assertEqual([],self.stored()['comparisons']);expect(self.page.get_by_role('article',name='Chosen plan to keep')).to_have_count(0)
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click();expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=10000);self.assertEqual(['POST','GET','GET'],self.calls)
  self.page.get_by_role('button',name='Edit Corrected owned lip',exact=True).click();self.page.get_by_label('Approximate color',exact=True).fill('#112233');self.page.get_by_role('button',name='Save product changes',exact=True).click();expect(self.page.get_by_role('button',name='Check / refresh existing task',exact=True)).to_have_count(0);expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_enabled();self.assertEqual(before,self.stored()['tasks']);self.assertEqual(['POST','GET','GET'],self.calls);self.assertEqual([],self.errors)
 def test_camera_input_preparation_invalid_success(self):
  self.add('Owned lip');cam=self.page.get_by_label('Take a selfie on this device',exact=True);self.assertEqual('user',cam.get_attribute('capture'));self.assertEqual('image/*',cam.get_attribute('accept'))
  cam.set_input_files({'name':'small.png','mimeType':'image/png','buffer':png(320,480)});expect(self.page.locator('.planner-message[role="status"]')).to_contain_text('short side remains at least 480');expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_disabled()
  cam.set_input_files({'name':'camera.heic','mimeType':'image/heic','buffer':b'unsupported fixture'});expect(self.page.locator('.planner-message[role="status"]')).to_contain_text('JPEG or PNG');expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_disabled()
  cam.set_input_files({'name':'broken.jpg','mimeType':'image/jpeg','buffer':b'not an image'});expect(self.page.locator('.planner-message[role="status"]')).to_contain_text('source image cannot be decoded');expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_disabled()
  cam.set_input_files({'name':'valid.png','mimeType':'image/png','buffer':png(1200,1600)});expect(self.page.locator('.planner-message[role="status"]')).to_contain_text('Prepared 768 × 1024 JPEG');self.assertIsNotNone(self.stored()['sourceHash']);expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_disabled();self.page.get_by_label(re.compile('I have permission')).check();expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_enabled();self.assertEqual([],self.calls);self.assertEqual([],self.errors)
if __name__=='__main__':unittest.main(verbosity=2)

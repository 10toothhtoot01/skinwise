"""Reusable kit contract and stale-read probes. Fictional fixtures; API mocked/zero calls."""
import json,re,unittest
from pathlib import Path
from playwright.sync_api import expect
import browser_planner as b
E=Path('../../work/qa-practical');E.mkdir(parents=True,exist_ok=True)
def kit(name='Imported lip',color='#123456',sample=False):
 return {'version':1,'sample':sample,'products':[{'id':'kit-lip','name':name,'category':'lip_color','color':color,'minutes':2}]}
class Kit(unittest.TestCase):
 setUpClass=classmethod(b.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(b.PlannerAcceptance.tearDownClass.__func__)
 setUp=b.PlannerAcceptance.setUp
 stored=b.PlannerAcceptance.stored
 add=b.PlannerAcceptance.add
 def tearDown(self):
  self.page.screenshot(path=str(E/(self._testMethodName+'.png')),full_page=True)
  (E/(self._testMethodName+'.json')).write_text(json.dumps({'uncaughtErrors':self.errors,'mockApiMethods':self.calls,'paidProviderCalls':0},indent=2));self.context.close()
 def open(self):
  if self.page.locator('.planner-kit-file').get_attribute('open') is None:self.page.get_by_text('Keep your kit for another visit',exact=True).click()
 def upload(self,value,name='kit.json'):
  self.open();self.page.get_by_label('Restore kit file',exact=True).set_input_files({'name':name,'mimeType':'application/json','buffer':json.dumps(value).encode()})
 def delay(self):
  self.page.evaluate("""()=>{window.__kitReads=[];const original=File.prototype.text;File.prototype.text=function(){return original.call(this).then(value=>new Promise(resolve=>window.__kitReads.push(()=>resolve(value))))}}""")
 def release(self,index=0):self.page.evaluate('(index)=>window.__kitReads[index]()',index)
 def test_kit_file_minimal_roundtrip_invalid_preserves(self):
  self.add('Entered owned lip');self.open()
  with self.page.expect_download() as dl:self.page.get_by_role('button',name='Save kit file',exact=True).click()
  data=json.loads(Path(dl.value.path()).read_text());self.assertEqual({'version','sample','products'},set(data));self.assertEqual('Entered owned lip',data['products'][0]['name'])
  self.page.on('dialog',lambda d:d.accept());self.upload(kit(sample=True));expect(self.page.get_by_role('button',name='Remove Imported lip',exact=True)).to_be_visible();self.assertTrue(self.stored()['sample']);self.assertEqual([],self.stored()['tasks']);self.assertIsNone(self.stored()['selected'])
  invalid=kit('Invalid');invalid['products'][0]['color']='bad';self.upload(invalid);expect(self.page.get_by_role('status').filter(has_text='not a valid kit file')).to_be_visible();self.assertEqual('Imported lip',self.stored()['products'][0]['name']);self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_latest_kit_read_wins(self):
  self.delay();self.page.on('dialog',lambda d:d.accept());self.upload(kit('Older'));self.page.wait_for_function('window.__kitReads.length===1');self.upload(kit('Newest'));self.page.wait_for_function('window.__kitReads.length===2');self.release(1);expect(self.page.get_by_role('button',name='Remove Newest',exact=True)).to_be_visible();self.release(0);self.page.wait_for_timeout(100);self.assertEqual('Newest',self.stored()['products'][0]['name']);self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_clear_empty_session_cancels_pending_kit(self):
  self.delay();self.page.on('dialog',lambda d:d.accept());self.upload(kit('Stale import'));self.page.wait_for_function('window.__kitReads.length===1');self.page.get_by_role('button',name='Clear session',exact=True).click();self.release();self.page.wait_for_timeout(150);self.assertEqual([], (self.stored() or {}).get('products',[]));expect(self.page.get_by_role('button',name='Remove Stale import',exact=True)).to_have_count(0);self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_same_metadata_recovery_cancels_pending_kit(self):
  self.page.get_by_text('Private recovery files',exact=True).click()
  with self.page.expect_download() as dl:self.page.get_by_role('button',name='Save private recovery file',exact=True).click()
  recovery=Path(dl.value.path()).read_bytes()
  self.delay();self.page.on('dialog',lambda d:d.accept());self.upload(kit('Stale recovery import'));self.page.wait_for_function('window.__kitReads.length===1')
  self.page.get_by_label('Restore a private recovery file',exact=True).set_input_files({'name':'recovery.json','mimeType':'application/json','buffer':recovery});self.page.wait_for_function('window.__kitReads.length===2');self.release(1)
  expect(self.page.get_by_role('status').filter(has_text='Recovery file restored')).to_be_visible();self.release(0);self.page.wait_for_timeout(150);self.assertEqual([],self.stored()['products']);expect(self.page.get_by_role('button',name='Remove Stale recovery import',exact=True)).to_have_count(0);self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_restored_kit_preserves_receipt_and_mobile_layout(self):
  self.page.set_viewport_size({'width':390,'height':844});self.add('Initial lip')
  b.PlannerAcceptance.photo(self);self.page.get_by_label(re.compile('I have permission')).check();self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).click();expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=15000)
  prior=self.stored();restored=kit('Renamed same color',prior['products'][0]['color']);restored['products'][0]['id']='different-owned-id';self.page.on('dialog',lambda d:d.accept());self.upload(restored);expect(self.page.get_by_role('button',name='Remove Renamed same color',exact=True)).to_be_visible();after=self.stored();self.assertEqual(prior['sourceHash'],after['sourceHash']);self.assertEqual(prior['tasks'],after['tasks']);self.assertIsNone(after['selected']);self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click();expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=15000);self.assertEqual(['POST','GET','GET'],self.calls);self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390);self.assertEqual([],self.errors)
if __name__=='__main__':unittest.main(verbosity=2)

"""Advice and private observations. Fictional fixtures, provider blocked."""
import json,unittest
from pathlib import Path
from playwright.sync_api import expect
import browser_planner as base
KEY='skinwise-private-observations-v1'
OUT=Path('../../work/qa-practical');OUT.mkdir(parents=True,exist_ok=True)
class PlannerEvidence(unittest.TestCase):
 setUpClass=classmethod(base.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(base.PlannerAcceptance.tearDownClass.__func__)
 setUp=base.PlannerAcceptance.setUp
 add=base.PlannerAcceptance.add
 def tearDown(self):
  self.page.screenshot(path=str(OUT/(self._testMethodName+'.png')),full_page=True)
  (OUT/(self._testMethodName+'.json')).write_text(json.dumps({'uncaughtErrors':self.errors,'mockApiMethods':self.calls},indent=2));self.context.close()
 def notes(self):return self.page.locator('.planner-observations')
 def fill(self):
  self.add('Fixture owned lip');self.notes().get_by_label('Product you tried').select_option(index=1)
  self.notes().get_by_label('Use conditions or occasion').fill('Fictional indoor QA')
  self.notes().get_by_label('Your observation',exact=True).fill('Fixture only: brush difficult, no physical-use claim.')
 def test_advice_requires_context_and_zero_reviews(self):
  section=self.page.locator('section[aria-labelledby="guidance-title"]')
  for option in ['lip-edge','blush-placement','shadow-edge']:
   section.get_by_label('Technique question').select_option(option)
   expect(section).to_contain_text('Check applicability first:');section.get_by_role('checkbox').check()
   expect(section).to_contain_text('When this helps:');expect(section).to_contain_text('Limits:')
  section.get_by_text('Reviews and tips: evidence available',exact=True).click()
  expect(section).to_contain_text('No verified external reviews or community tips');self.assertEqual([],self.calls)
 def test_explicit_save_reload_export_and_delete_confirmation(self):
  self.fill();self.assertIsNone(self.page.evaluate('(k)=>localStorage.getItem(k)',KEY))
  self.notes().get_by_role('button',name='Save private observation',exact=True).click();expect(self.notes()).to_contain_text('1 private observations.')
  self.page.reload();self.page.wait_for_load_state('networkidle');expect(self.notes()).to_contain_text('Fixture only: brush difficult')
  with self.page.expect_download() as event:self.notes().get_by_role('button',name='Export private observations',exact=True).click()
  data=json.loads(Path(event.value.path()).read_text());self.assertEqual('private-self-reported',data['source']);self.assertEqual(1,len(data['notes']))
  self.page.once('dialog',lambda d:d.dismiss());self.notes().get_by_role('button',name='Delete observation',exact=True).click();expect(self.notes()).to_contain_text('1 private observations.')
  self.page.once('dialog',lambda d:d.accept());self.notes().get_by_role('button',name='Delete all observations',exact=True).click();expect(self.notes()).to_contain_text('0 private observations.')
  self.assertIsNone(self.page.evaluate('(k)=>localStorage.getItem(k)',KEY));self.assertEqual([],self.calls)
 def test_corrupt_bytes_preserved_exportable(self):
  raw='{invalid QA observations';self.page.evaluate('([k,v])=>localStorage.setItem(k,v)',[KEY,raw]);self.page.reload();self.page.wait_for_load_state('networkidle')
  expect(self.notes()).to_contain_text('Existing bytes are preserved');self.fill();expect(self.notes().get_by_role('button',name='Save private observation',exact=True)).to_be_disabled()
  with self.page.expect_download() as event:self.notes().get_by_role('button',name='Export original observations',exact=True).click()
  self.assertEqual(raw,Path(event.value.path()).read_text());self.assertEqual(raw,self.page.evaluate('(k)=>localStorage.getItem(k)',KEY));self.assertEqual([],self.calls)
 def test_storage_failure_and_fictional_kit(self):
  self.fill();self.page.evaluate("() => {const original=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='skinwise-private-observations-v1')throw new DOMException('QA quota','QuotaExceededError');return original.call(this,k,v)}}")
  self.notes().get_by_role('button',name='Save private observation',exact=True).click();expect(self.notes()).to_contain_text('This browser could not confirm the saved change');expect(self.notes()).to_contain_text('0 private observations.')
  self.page.evaluate('()=>sessionStorage.clear()');self.page.reload();self.page.wait_for_load_state('networkidle')
  self.page.get_by_role('button',name='Try the solver with a clearly fictional kit',exact=True).click();self.notes().get_by_label('Product you tried').select_option(index=1);self.notes().get_by_label('Your observation',exact=True).fill('Fixture must never save')
  expect(self.notes().get_by_role('button',name='Save private observation',exact=True)).to_be_disabled();self.assertIsNone(self.page.evaluate('(k)=>localStorage.getItem(k)',KEY));self.assertEqual([],self.calls)

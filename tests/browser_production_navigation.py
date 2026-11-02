"""Production routing/readiness boundaries. All provider operations mocked; no paid requests."""
import json
import re
import unittest
from pathlib import Path
from playwright.sync_api import expect
import browser_planner as b

E=Path('../../work/qa-production');E.mkdir(parents=True,exist_ok=True)

class ProductionNavigation(unittest.TestCase):
 setUpClass=classmethod(b.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(b.PlannerAcceptance.tearDownClass.__func__)
 setUp=b.PlannerAcceptance.setUp
 add=b.PlannerAcceptance.add
 photo=b.PlannerAcceptance.photo
 stored=b.PlannerAcceptance.stored
 export=b.PlannerAcceptance.export
 def tearDown(self):
  self.page.screenshot(path=str(E/(self._testMethodName+'.png')),full_page=True)
  (E/(self._testMethodName+'-safe.json')).write_text(json.dumps({'uncaughtErrors':self.errors,'mockMakeupMethods':self.calls,'paidProviderRequests':0,'urlPath':self.page.url.split(b.BASE)[-1]},indent=2))
  self.context.close()
 def status(self,mode):
  def route(r):
   if mode=='transport':r.abort()
   elif mode=='malformed':r.fulfill(json={'configured':'yes'})
   elif mode=='http-error':r.fulfill(status=503,json={'configured':True})
   else:r.fulfill(json={'configured':mode})
  self.page.route('**/api/status',route)
  self.page.reload();self.page.wait_for_load_state('networkidle')
 def test_root_journal_navigation_preserves_separate_storage(self):
  self.page.goto(b.BASE+'/');self.page.wait_for_load_state('networkidle');expect(self.page).to_have_url(b.BASE+'/planner')
  self.add('Navigation QA lip');self.page.get_by_role('button',name='Choose no added makeup',exact=True).click();before=self.stored()
  self.page.get_by_role('link',name='Skin journal',exact=True).click();expect(self.page).to_have_url(b.BASE+'/journal');expect(self.page.get_by_role('heading',name='A good day to know your skin.')).to_be_visible()
  self.page.get_by_role('navigation',name='Main navigation').get_by_role('button',name=re.compile(r'^My journal')).click();self.page.get_by_label('Your observation',exact=True).fill('Navigation QA self-report');self.page.get_by_role('button',name='Save check-in',exact=True).click();expect(self.page.get_by_text('Navigation QA self-report',exact=True)).to_be_visible()
  self.page.get_by_role('link',name='Own-kit look lab',exact=True).click();expect(self.page).to_have_url(b.BASE+'/planner');self.assertEqual(before,self.stored())
  self.page.goto(b.BASE+'/journal');self.page.wait_for_load_state('networkidle');self.page.get_by_role('navigation',name='Main navigation').get_by_role('button',name=re.compile(r'^My journal')).click();expect(self.page.get_by_text('Navigation QA self-report',exact=True)).to_be_visible()
  self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_unconfigured_blocks_new_start_but_free_export_and_recheck_work(self):
  self.status(False);expect(self.page.locator('.workspace-status')).to_have_text('Preview API not configured');self.add();self.photo();self.page.get_by_label('I have permission',exact=False).check()
  button=self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True);expect(button).to_be_disabled()
  # Assert the handler independently enforces readiness, when called directly through its React event binding.
  button.evaluate('(e)=>{const key=Object.keys(e).find(k=>k.startsWith("__reactProps$"));if(!key)throw Error("React handler unavailable");e[key].onClick()}');expect(self.page.get_by_role('status').filter(has_text='New previews are paused')).to_be_visible();self.assertEqual([],self.calls)
  self.page.get_by_text('Browse all 1 feasible combinations',exact=True).click();self.page.get_by_role('button',name='Choose without preview',exact=True).click();data=self.export();self.assertEqual('constraints-only',data['selectionBasis']);self.assertEqual('My rose lip',data['selected']['products'][0]['name'])
  self.page.route('**/api/status',lambda r:r.fulfill(json={'configured':True}));self.page.get_by_role('button',name='Recheck preview connection',exact=True).click();expect(self.page.locator('.workspace-status')).to_have_text('Preview API configured');expect(button).to_be_enabled();self.assertEqual([],self.calls);self.assertEqual([],self.errors)
 def test_invalid_or_unavailable_status_abstains_and_can_recheck(self):
  self.add();self.photo();self.page.get_by_label('I have permission',exact=False).check()
  for mode in ['malformed','transport','http-error']:
   with self.subTest(mode=mode):
    self.status(mode);expect(self.page.locator('.workspace-status')).to_have_text('Preview API status unavailable');self.photo();self.page.get_by_label('I have permission',exact=False).check();expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_disabled();self.assertEqual([],self.calls)
  self.page.route('**/api/status',lambda r:r.fulfill(json={'configured':True}));self.page.get_by_role('button',name='Recheck preview connection',exact=True).click();expect(self.page.locator('.workspace-status')).to_have_text('Preview API configured');expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_enabled();self.assertEqual([],self.errors)
 def test_existing_receipt_get_allowed_without_new_start_readiness(self):
  self.add();self.photo();self.page.get_by_label('I have permission',exact=False).check();self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).click();expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=15000);self.assertEqual(['POST','GET'],self.calls)
  before=self.stored()['tasks'];self.status(False);expect(self.page.get_by_role('button',name='Check / refresh existing task',exact=True)).to_be_enabled();self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click();expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=10000);self.assertEqual(['POST','GET','GET'],self.calls);self.assertEqual(before,self.stored()['tasks']);self.assertEqual([],self.errors)

if __name__=='__main__':unittest.main(verbosity=2)

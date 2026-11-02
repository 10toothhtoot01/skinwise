"""Explicit invalid-receipt recovery; all provider responses mocked, zero paid calls."""
import unittest
from playwright.sync_api import expect
import browser_planner as base

class PlannerExpiry(unittest.TestCase):
 setUpClass=classmethod(base.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(base.PlannerAcceptance.tearDownClass.__func__)
 setUp=base.PlannerAcceptance.setUp
 tearDown=base.PlannerAcceptance.tearDown
 stored=base.PlannerAcceptance.stored
 ready=base.PlannerAcceptance.ready
 add=base.PlannerAcceptance.add
 photo=base.PlannerAcceptance.photo
 render=base.PlannerAcceptance.render
 clean=base.PlannerAcceptance.clean
 export=base.PlannerAcceptance.export
 def invalid(self, status=403, code='INVALID_TASK'):
  self.page.unroute('**/api/makeup*')
  def fail(route):
   self.calls.append(route.request.method)
   route.fulfill(status=status,json={'error':'Saved receipt unavailable.','code':code})
  self.page.route('**/api/makeup*',fail)
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('status').filter(has_text='Saved receipt unavailable.')).to_be_visible()
 def forget(self):return self.page.get_by_role('button',name='Forget this preview receipt',exact=True)
 def test_visible_starter_can_be_chosen_and_exported_without_photo(self):
  self.page.set_viewport_size({'width':390,'height':844});self.add()
  self.page.get_by_role('button',name='Choose without a photo',exact=True).click()
  result=self.export();self.assertEqual('constraints-only',result['selectionBasis'])
  self.assertEqual('My rose lip',result['selected']['products'][0]['name'])
  self.assertEqual(3,result['selected']['estimatedMinutes'])
  self.assertEqual([],self.calls);self.assertIsNone(self.stored()['sourceHash']);self.clean()
 def test_explicit_forget_preserves_free_choice_and_other_receipts(self):
  self.ready();self.render()
  self.page.evaluate('(key)=>{const m=JSON.parse(sessionStorage.getItem(key));m.tasks.unshift({...m.tasks[0],taskId:"other-receipt"});sessionStorage.setItem(key,JSON.stringify(m));}',base.KEY)
  self.page.reload();self.page.wait_for_load_state('networkidle')
  self.page.get_by_role('button',name='Choose no added makeup',exact=True).click()
  before=self.stored();self.invalid()
  expect(self.forget()).to_be_visible()
  self.page.once('dialog',lambda dialog:dialog.dismiss());self.forget().click()
  self.assertEqual(before,self.stored())
  self.page.once('dialog',lambda dialog:dialog.accept());self.forget().click()
  after=self.stored();self.assertEqual(before['tasks'][:1],after['tasks'])
  for key in ['products','rules','sourceHash','selected','selectionBasis','event']:
   self.assertEqual(before[key],after[key])
  self.assertEqual(['POST','GET','GET'],self.calls)
  self.page.unroute('**/api/makeup*')
  def success(route):
   self.calls.append(route.request.method)
   self.assertIn('other-receipt',route.request.url)
   route.fulfill(json={'status':'success','url':base.AWS})
  self.page.route('**/api/makeup*',success)
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled()
  self.assertEqual(['POST','GET','GET','GET'],self.calls);self.clean()
 def test_forget_invalidates_visual_choice_and_comparisons_without_new_start(self):
  self.ready();self.render()
  self.page.get_by_role('button',name='Prefer right',exact=True).click()
  self.page.get_by_role('button',name='Choose this plan',exact=True).click()
  self.assertEqual('loaded-preview',self.stored()['selectionBasis'])
  self.invalid();self.page.once('dialog',lambda dialog:dialog.accept());self.forget().click()
  state=self.stored();self.assertEqual([],state['tasks']);self.assertEqual([],state['comparisons']);self.assertIsNone(state['selected'])
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_have_count(0)
  self.assertEqual(['POST','GET','GET'],self.calls)
  # The action does not start a task; after reload the normal portrait and consent gates apply.
  self.page.reload();self.page.wait_for_load_state('networkidle')
  expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_disabled()
  self.assertEqual(['POST','GET','GET'],self.calls);self.clean()
 def test_same_recipe_free_choice_survives_forgetting(self):
  self.ready();self.render()
  self.page.get_by_role('button',name='Choose without a photo',exact=True).click()
  before=self.stored();self.assertEqual('constraints-only',before['selectionBasis'])
  self.invalid();self.page.once('dialog',lambda dialog:dialog.accept());self.forget().click()
  self.assertEqual(before['selected'],self.stored()['selected']);self.assertEqual('constraints-only',self.stored()['selectionBasis'])
  self.assertEqual(['POST','GET','GET'],self.calls);self.clean()
 def test_reused_receipt_after_reload_clears_its_visual_choice(self):
  self.ready();self.render()
  self.page.get_by_label('Minutes available',exact=True).fill('9')
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled()
  self.page.get_by_role('button',name='Choose this plan',exact=True).click()
  self.assertNotEqual(self.stored()['tasks'][0]['key'],self.stored()['selected'])
  self.page.reload();self.page.wait_for_load_state('networkidle')
  self.invalid();self.page.once('dialog',lambda dialog:dialog.accept());self.forget().click()
  self.assertIsNone(self.stored()['selected']);self.assertEqual([],self.stored()['tasks'])
  self.assertEqual(['POST','GET','GET','GET'],self.calls);self.clean()
 def test_transient_failure_never_offers_forgetting(self):
  self.ready();self.render()
  for status,code in [(429,'RATE_LIMIT'),(503,'PROVIDER_UNAVAILABLE'),(403,'OTHER_ERROR')]:
   self.invalid(status,code);expect(self.forget()).to_have_count(0)
   self.assertEqual(1,len(self.stored()['tasks']))
  self.page.unroute('**/api/makeup*');self.page.route('**/api/makeup*',lambda route:route.abort('timedout'))
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('button',name='Check / refresh existing task',exact=True)).to_be_enabled()
  expect(self.forget()).to_have_count(0);self.assertEqual(1,len(self.stored()['tasks']));self.clean()

if __name__=='__main__':unittest.main(verbosity=2)

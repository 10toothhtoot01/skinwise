"""Paid-task reuse by exact render identity. Mock-only; never spends API units.
PYTHONPATH=tests python -m unittest -v browser_planner_reuse
"""
import json
import re
import unittest
from playwright.sync_api import expect
import browser_planner as base

class PlannerReuse(unittest.TestCase):
 setUpClass=classmethod(base.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(base.PlannerAcceptance.tearDownClass.__func__)
 setUp=base.PlannerAcceptance.setUp
 tearDown=base.PlannerAcceptance.tearDown
 stored=base.PlannerAcceptance.stored
 add=base.PlannerAcceptance.add
 photo=base.PlannerAcceptance.photo
 ready=base.PlannerAcceptance.ready
 render=base.PlannerAcceptance.render
 clean=base.PlannerAcceptance.clean
 def check_existing(self):
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=10000)
 def rewrite_session(self,script):
  self.page.evaluate('(key)=>{const model=JSON.parse(sessionStorage.getItem(key));'+script+';sessionStorage.setItem(key,JSON.stringify(model))}',base.KEY)
  self.page.reload();self.page.wait_for_load_state('networkidle')
 def test_rules_only_change_reuses_task_without_alias_receipts(self):
  self.ready();self.render();before=self.stored();source=before['sourceHash']
  snapshot=json.loads(before['tasks'][0]['renderIdentity'])
  self.assertEqual('owned-kit-matte-v1',snapshot['version'])
  self.assertEqual(['skin_smooth','lip_color'],[effect['category'] for effect in snapshot['effects']])
  self.page.get_by_label('Minutes available',exact=True).fill('9')
  expect(self.page.get_by_role('button',name='Check / refresh existing task',exact=True)).to_be_visible()
  self.check_existing()
  after=self.stored();self.assertEqual(source,after['sourceHash'])
  self.assertEqual(before['tasks'],after['tasks'])
  self.assertEqual(['POST','GET','GET'],self.calls);self.clean()
 def test_legacy_receipt_without_identity_reuses_same_effects(self):
  self.ready();self.render()
  self.rewrite_session("delete model.tasks[0].renderIdentity;model.rules.maxMinutes=9")
  self.check_existing()
  self.assertEqual(1,len(self.stored()['tasks']))
  self.assertEqual(['POST','GET','GET'],self.calls);self.clean()
 def test_product_metadata_changes_reuse_but_color_and_category_do_not(self):
  self.ready();self.render();before=self.stored()
  self.rewrite_session("model.products[0]={...model.products[0],id:'renamed-owned-item',name:'Renamed owned product',minutes:2};model.selected=null;model.selectionBasis=null;model.previewFocus=null;model.comparisons=[]")
  self.check_existing();self.assertEqual(before['tasks'],self.stored()['tasks'])
  self.assertEqual(['POST','GET','GET'],self.calls)
  self.rewrite_session("model.products[0].color='#123456'")
  expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_visible()
  expect(self.page.get_by_role('button',name='Check / refresh existing task',exact=True)).to_have_count(0)
  self.rewrite_session("model.products[0].color='#a44357';model.products[0].category='blush'")
  expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_visible()
  expect(self.page.get_by_role('button',name='Check / refresh existing task',exact=True)).to_have_count(0)
  self.assertEqual(['POST','GET','GET'],self.calls);self.clean()
 def test_changed_portrait_invalidates_matching_effect_receipt(self):
  self.ready();self.render();source=self.stored()['sourceHash']
  self.page.once('dialog',lambda dialog:dialog.accept());self.photo(other=True)
  self.assertNotEqual(source,self.stored()['sourceHash']);self.assertEqual([],self.stored()['tasks'])
  expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_visible()
  expect(self.page.get_by_role('button',name='Check / refresh existing task',exact=True)).to_have_count(0)
  self.assertEqual(['POST','GET'],self.calls);self.clean()
 def test_full_task_cap_allows_existing_render_check(self):
  self.ready();self.render()
  self.rewrite_session("const saved=model.tasks[0];model.tasks=[saved,...Array.from({length:49},(_,i)=>({...saved,key:'earlier-'+i,taskId:'mock-earlier-'+i}))];model.rules.maxMinutes=9")
  self.check_existing()
  self.assertEqual(50,len(self.stored()['tasks']));self.assertEqual(['POST','GET','GET'],self.calls);self.clean()
 def test_stored_different_render_snapshot_is_not_reused(self):
  self.ready();self.render()
  self.rewrite_session("model.tasks[0].renderIdentity='different-render-version-and-effects'")
  expect(self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)).to_be_visible()
  expect(self.page.get_by_role('button',name='Check / refresh existing task',exact=True)).to_have_count(0)
  self.assertEqual(['POST','GET'],self.calls);self.clean()

if __name__=='__main__':unittest.main(verbosity=2)

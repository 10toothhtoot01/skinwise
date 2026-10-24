"""Free all-feasible decisions and optional rendering. Mock-only; no paid calls.
PYTHONPATH=tests python -m unittest -v browser_planner_decision
"""
import json
import re
import unittest
from pathlib import Path
from playwright.sync_api import expect
import browser_planner as base

class PlannerDecision(unittest.TestCase):
 setUpClass=classmethod(base.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(base.PlannerAcceptance.tearDownClass.__func__)
 setUp=base.PlannerAcceptance.setUp
 tearDown=base.PlannerAcceptance.tearDown
 stored=base.PlannerAcceptance.stored
 add=base.PlannerAcceptance.add
 photo=base.PlannerAcceptance.photo
 export=base.PlannerAcceptance.export
 clean=base.PlannerAcceptance.clean
 def kit(self):
  for name,category,minutes in [('Owned rose','lip_color',3),('Owned coral','lip_color',2),('Owned cheek','blush',4),('Owned eye','eye_shadow',5)]:self.add(name,category,minutes)
  self.page.get_by_label('Minutes available',exact=True).fill('20')
  self.page.locator('.planner-inputs section').first.locator('select').select_option('3')
  expect(self.page.get_by_role('heading',name='11 feasible combinations',exact=True)).to_be_visible()
 def catalog(self):
  expect(self.page.get_by_text('Browse all 11 feasible combinations',exact=True)).to_be_visible()
  self.page.get_by_text('Browse all 11 feasible combinations',exact=True).click()
  expect(self.page.locator('.planner-catalog li')).to_have_count(11)
 def row(self,*names):
  row=self.page.locator('.planner-catalog li')
  for name in names:row=row.filter(has_text=name)
  expect(row).to_have_count(1)
  return row
 def card(self,*names):
  card=self.page.locator('.planner-cards article')
  for name in names:card=card.filter(has_text=name)
  expect(card).to_have_count(1)
  return card
 def choose_omitted(self):
  self.row('Owned rose','Owned cheek','Owned eye').get_by_role('button',name='Choose without preview',exact=True).click()
 def test_all_feasible_recipes_free_choice_export_reload_and_no_makeup(self):
  self.kit();self.catalog();self.choose_omitted()
  expect(self.page.locator('.planner-handoff')).to_contain_text('Chosen without requiring a preview')
  result=self.export()
  self.assertEqual('constraints-only',result['selectionBasis'])
  self.assertEqual(['Owned rose','Owned cheek','Owned eye'],[p['name'] for p in result['selected']['products']])
  self.assertEqual(12,result['selected']['estimatedMinutes'])
  self.assertEqual(['skin_smooth','lip_color','blush','eye_shadow'],[e['category'] for e in result['selected']['digitalEffects']])
  self.assertEqual([],self.calls)
  self.page.reload();self.page.wait_for_load_state('networkidle')
  self.assertEqual(result['selected'],self.export()['selected'])
  self.assertEqual('constraints-only',self.export()['selectionBasis'])
  self.page.get_by_role('button',name='Choose no added makeup',exact=True).click()
  no_makeup=self.export();self.assertEqual('No added makeup',no_makeup['selected']);self.assertEqual('original',no_makeup['selectionBasis'])
  self.assertEqual([],self.calls);self.clean()
 def test_optional_focus_correct_recipe_loaded_choice_and_get_only_return(self):
  self.kit();self.catalog();posted=[]
  def capture(route):
   if route.request.method=='POST':
    body=route.request.post_data_buffer.decode('latin1')
    posted.append(re.search(r'name="recipeId"\r\n\r\n([^\r]+)',body).group(1))
   route.fallback()
  self.page.route('**/api/makeup*',capture)
  self.row('Owned rose','Owned cheek','Owned eye').get_by_role('button',name='Open optional preview',exact=True).click()
  expect(self.page.locator('.planner-cards article')).to_have_count(4)
  self.assertEqual([],self.calls)
  self.photo();self.page.get_by_label(re.compile('I have permission')).check()
  focused=self.card('Owned rose','Owned cheek','Owned eye')
  focused.get_by_role('button',name='Preview this option · 1 unit',exact=True).click()
  expect(focused.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=15000)
  focused.get_by_role('button',name='Choose this plan',exact=True).click()
  self.assertEqual('loaded-preview',self.export()['selectionBasis'])
  products=self.stored()['products'];expected='+'.join(next(p['id'] for p in products if p['name']==n) for n in ['Owned rose','Owned cheek','Owned eye'])
  self.assertEqual([expected],posted);self.assertEqual(['POST','GET'],self.calls)
  self.row('Owned coral','Owned cheek','Owned eye').get_by_role('button',name='Open optional preview',exact=True).click()
  expect(self.page.locator('.planner-cards article')).to_have_count(5)
  self.row('Owned rose','Owned cheek','Owned eye').get_by_role('button',name='Open optional preview',exact=True).click()
  self.card('Owned rose','Owned cheek','Owned eye').get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.card('Owned rose','Owned cheek','Owned eye').get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=10000)
  self.assertEqual(['POST','GET','GET'],self.calls);self.assertEqual(1,len(self.stored()['tasks']));self.clean()
 def test_failed_optional_image_keeps_constraints_only_choice(self):
  self.kit();self.catalog();self.photo();self.page.get_by_label(re.compile('I have permission')).check()
  self.choose_omitted();chosen=self.stored()['selected'];self.expired=True
  self.row('Owned rose','Owned cheek','Owned eye').get_by_role('button',name='Open optional preview',exact=True).click()
  focused=self.card('Owned rose','Owned cheek','Owned eye')
  focused.get_by_role('button',name='Preview this option · 1 unit',exact=True).click()
  expect(focused.get_by_text('Temporary image unavailable. Check the existing task to refresh it.',exact=True)).to_be_visible(timeout=15000)
  self.assertEqual(chosen,self.stored()['selected']);self.assertEqual('constraints-only',self.export()['selectionBasis'])
  self.assertEqual(['Owned rose','Owned cheek','Owned eye'],[p['name'] for p in self.export()['selected']['products']])
  expect(focused.get_by_role('button',name='Choose this plan',exact=True)).to_be_disabled()
  self.assertEqual(['POST','GET'],self.calls);self.clean()
 def test_comparison_cap_preserves_session_and_reset_recovers(self):
  self.add('Owned lip');self.add('Owned cheek','blush',4);self.photo();self.page.get_by_label(re.compile('I have permission')).check()
  first=self.page.locator('.planner-cards article').nth(1)
  first.get_by_role('button',name='Preview this option · 1 unit',exact=True).click()
  expect(first.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=15000)
  self.page.evaluate('''key=>{const model=JSON.parse(sessionStorage.getItem(key));model.comparisons=Array.from({length:100},()=>({a:'original',b:model.tasks[0].key,choice:'tie'}));sessionStorage.setItem(key,JSON.stringify(model));}''',base.KEY)
  self.page.reload();self.page.wait_for_load_state('networkidle');self.photo()
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=10000)
  self.page.get_by_label(re.compile('I have permission')).check()
  other=self.page.locator('.planner-cards article').nth(2)
  other.get_by_role('button',name='Preview this option · 1 unit',exact=True).click()
  expect(other.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=15000)
  for label in ['Prefer left','Prefer right','Tie / cannot decide','Neither works']:
   button=self.page.get_by_role('button',name=label,exact=True);expect(button).to_be_disabled();button.dispatch_event('click')
  self.assertEqual(100,len(self.stored()['comparisons']))
  self.assertEqual(100,len(self.export()['comparisons']))
  self.page.get_by_role('button',name='Reset comparisons',exact=True).click()
  self.assertEqual([],self.stored()['comparisons'])
  expect(self.page.get_by_role('button',name='Prefer left',exact=True)).to_be_enabled()
  self.clean()

if __name__=='__main__':unittest.main(verbosity=2)

"""Own-kit planner acceptance. All API/image responses mocked; no paid calls.
PYTHONPATH=tests python -m unittest -v browser_planner
"""
import json
import os
import re
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from browser_capture import png

BASE=os.environ.get('SKINWISE_BASE_URL','http://127.0.0.1:5173')
KEY='skinwise-owned-kit-session-v1'
AWS='https://planner-fixtures.s3.amazonaws.com/result.png'
TOKEN='1799999999999.'+'a'*64
EVIDENCE=Path('../../work/qa-planner');EVIDENCE.mkdir(parents=True,exist_ok=True)

class PlannerAcceptance(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch(headless=True)
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.p.stop()
 def setUp(self):
  self.context=self.browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
  self.page=self.context.new_page();self.errors=[];self.calls=[];self.expired=False
  self.page.on('pageerror',lambda e:self.errors.append(str(e)))
  def api(route):
   self.calls.append(route.request.method)
   if route.request.method=='POST':route.fulfill(status=202,json={'status':'running','taskId':'mock-planner-task','token':TOKEN,'units':1})
   else:route.fulfill(json={'status':'success','url':AWS})
  self.page.route('**/api/status',lambda route:route.fulfill(json={'configured':True}))
  self.page.route('**/api/makeup*',api)
  self.page.route('https://planner-fixtures.s3.amazonaws.com/**',lambda r:r.fulfill(status=403 if self.expired else 200,content_type='image/png',body=b'expired' if self.expired else png(32,32)))
  # Block any direct provider call even if an implementation regression introduces one.
  self.page.route('https://yce-api-01.makeupar.com/**',lambda r:r.abort())
  self.page.goto(BASE+'/planner');self.page.wait_for_load_state('networkidle')
  expect(self.page.get_by_role('heading',name='A look you can plan with what you own.')).to_be_visible()
 def tearDown(self):
  self.page.screenshot(path=str(EVIDENCE/(self._testMethodName+'.png')),full_page=True)
  (EVIDENCE/(self._testMethodName+'.json')).write_text(json.dumps({'uncaughtErrors':self.errors,'mockApiMethods':self.calls},indent=2))
  self.context.close()
 def stored(self):return self.page.evaluate('(key)=>JSON.parse(sessionStorage.getItem(key))',KEY)
 def add(self,name='My rose lip',category='lip_color',minutes=3):
  self.page.get_by_label('Product name',exact=True).fill(name)
  self.page.locator('.planner-inputs form select').select_option(category)
  self.page.get_by_label('Your minutes',exact=True).fill(str(minutes))
  self.page.get_by_role('button',name='Add owned product',exact=True).click()
  expect(self.page.get_by_role('button',name='Remove '+name,exact=True)).to_be_visible()
 def photo(self,other=False):
  self.page.get_by_label('Portrait for visual rehearsal',exact=True).set_input_files({'name':'portrait.png','mimeType':'image/png','buffer':png(700 if other else 768,1024)})
  expect(self.page.get_by_role('status').filter(has_text='Prepared')).to_be_visible()
 def ready(self):
  self.add();self.photo();self.page.get_by_label(re.compile('I have permission')).check()
 def render(self):
  self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).first.click()
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=15000)
 def export(self):
  with self.page.expect_download() as event:self.page.get_by_role('button',name='Export plan and decision trail').click()
  return json.loads(Path(event.value.path()).read_text())
 def clean(self):self.assertEqual([],self.errors)
 def test_owned_constraints_explanations_and_fractional_time(self):
  self.add();self.add('My blush','blush',4)
  expect(self.page.get_by_role('heading',name='3 feasible combinations')).to_be_visible()
  lip=self.page.locator('.planner-category').filter(has_text='Lip color')
  lip.get_by_label('Required',exact=True).check();lip.get_by_label('Exclude',exact=True).check()
  expect(self.page.get_by_text('Lip color is both required and excluded.',exact=True)).to_be_visible()
  lip.get_by_label('Exclude',exact=True).uncheck()
  self.page.get_by_label('Minutes available',exact=True).fill('1.5')
  expect(self.page.get_by_role('heading',level=1)).to_be_visible()
  self.assertEqual(10,self.stored()['rules']['maxMinutes'])
  self.page.get_by_label('Minutes available',exact=True).fill('1')
  expect(self.page.get_by_text('The quickest eligible combination needs 3 minutes by your estimates; your limit is 1.',exact=True)).to_be_visible()
  self.assertEqual([],self.calls);self.clean()
 def test_paid_preview_get_only_resume_export_and_same_source(self):
  self.ready();self.render();self.assertEqual(['POST','GET'],self.calls)
  self.page.get_by_role('button',name='Choose this plan',exact=True).click()
  data=self.export();self.assertEqual('My rose lip',data['selected']['products'][0]['name'])
  self.assertIsNotNone(self.stored()['sourceHash'])
  text=json.dumps(data)
  for secret in [TOKEN,AWS,'taskId','token','sourceHash','data:image']:self.assertNotIn(secret,text)
  self.page.reload();self.page.wait_for_load_state('networkidle')
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=10000)
  self.assertEqual(['POST','GET','GET'],self.calls)
  self.photo();self.assertEqual(1,len(self.stored()['tasks']))
  self.assertEqual(['POST','GET','GET'],self.calls);self.clean()
 def test_rejection_and_changed_occasion_clear_decision(self):
  self.ready();self.render()
  self.page.get_by_role('button',name='Choose this plan',exact=True).click()
  self.page.get_by_role('button',name='Neither works',exact=True).click()
  self.assertIsNone(self.stored()['selected'])
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_disabled()
  self.assertIsNone(self.export()['selected'])
  self.page.reload();self.page.wait_for_load_state('networkidle')
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('img',name='YouCam preview for option 1',exact=True)).to_have_js_property('naturalWidth',32,timeout=10000)
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_disabled()
  self.photo()
  self.page.get_by_role('button',name='Reset comparisons',exact=True).click()
  self.page.get_by_role('button',name='Prefer right',exact=True).click()
  self.page.get_by_role('button',name='Choose this plan',exact=True).click()
  self.page.get_by_label('What are you getting ready for?',exact=True).fill('A different occasion')
  self.assertEqual([],self.stored()['comparisons']);self.assertIsNone(self.stored()['selected']);self.clean()
 def test_expired_image_is_not_comparable_or_selectable(self):
  self.expired=True;self.ready()
  self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).click()
  expect(self.page.get_by_text('Temporary image unavailable. Check the existing task to refresh it.',exact=True).first).to_be_visible(timeout=15000)
  choices=self.page.get_by_role('button',name='Choose this plan',exact=True)
  if choices.count():expect(choices).to_be_disabled()
  expect(self.page.get_by_role('button',name='Prefer right',exact=True)).to_have_count(0)
  self.assertIsNone(self.stored()['selected']);self.clean()
 def test_task_limit_blocks_post_preserves_receipts(self):
  self.ready()
  self.page.evaluate('''key=>{const m=JSON.parse(sessionStorage.getItem(key));m.tasks=Array.from({length:50},(_,i)=>({key:'previous-'+i,recipe:{id:'previous-'+i,key:'previous-'+i,products:[{...m.products[0],color:'#123456'}],minutes:3},taskId:'mock-'+i,token:'receipt-'+i}));sessionStorage.setItem(key,JSON.stringify(m));}''',KEY)
  self.page.reload();self.page.wait_for_load_state('networkidle');self.photo()
  self.page.get_by_label(re.compile('I have permission')).check()
  self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).click()
  expect(self.page.get_by_role('status').filter(has_text='50-task limit')).to_be_visible()
  self.assertEqual(50,len(self.stored()['tasks']));self.assertEqual([],self.calls);self.clean()
 def test_different_portrait_requires_confirmation_before_losing_receipts(self):
  self.ready();self.render();previous=self.stored()['sourceHash'];dialogs=[]
  def reject(dialog):dialogs.append(dialog.message);dialog.dismiss()
  self.page.once('dialog',reject)
  self.page.get_by_label('Portrait for visual rehearsal',exact=True).set_input_files({'name':'different.png','mimeType':'image/png','buffer':png(700,1024)})
  self.page.wait_for_timeout(500)
  self.assertEqual(1,len(dialogs));self.assertIn('different prepared portrait',dialogs[0])
  self.assertEqual(previous,self.stored()['sourceHash']);self.assertEqual(1,len(self.stored()['tasks']))
  self.page.once('dialog',lambda dialog:dialog.accept())
  self.page.get_by_label('Portrait for visual rehearsal',exact=True).set_input_files({'name':'different.png','mimeType':'image/png','buffer':png(700,1024)})
  self.page.wait_for_function('([key,previous])=>JSON.parse(sessionStorage.getItem(key)).sourceHash!==previous',arg=[KEY,previous])
  self.assertEqual([],self.stored()['tasks']);self.assertEqual(['POST','GET'],self.calls);self.clean()
 def test_mobile_fictional_solver_never_starts_paid_preview(self):
  self.page.set_viewport_size({'width':390,'height':844})
  self.page.get_by_role('button',name='Try the solver with a clearly fictional kit').click()
  expect(self.page.get_by_text(re.compile('Fictional kit: solver demonstration only'))).to_be_visible()
  self.photo();self.page.get_by_label(re.compile('I have permission')).check()
  for button in self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).all():expect(button).to_be_disabled()
  self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
  data=self.export();self.assertEqual('fictional-kit',data['source']);self.assertEqual([],self.calls);self.clean()

if __name__=='__main__':unittest.main(verbosity=2)

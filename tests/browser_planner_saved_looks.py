"""Private saved-look lifecycle. API calls are mocked; no paid-provider jobs.
PYTHONPATH=tests python -m unittest -v browser_planner_saved_looks
"""
import json,re,unittest
from pathlib import Path
from playwright.sync_api import expect
import browser_planner as base

KEY='skinwise-private-saved-looks-v1'
OUT=Path('../../work/qa-saved-looks');OUT.mkdir(parents=True,exist_ok=True)

class SavedLooks(unittest.TestCase):
 setUpClass=classmethod(base.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(base.PlannerAcceptance.tearDownClass.__func__)
 setUp=base.PlannerAcceptance.setUp
 add=base.PlannerAcceptance.add
 photo=base.PlannerAcceptance.photo
 stored=base.PlannerAcceptance.stored
 def tearDown(self):
  self.page.screenshot(path=str(OUT/(self._testMethodName+'.png')),full_page=True)
  (OUT/(self._testMethodName+'.json')).write_text(json.dumps({'uncaughtErrors':self.errors,'mockApiMethods':self.calls,'paidProviderCalls':0},indent=2));self.context.close()
 def section(self):return self.page.locator('#saved-looks')
 def saved(self):return self.page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',KEY)
 def choose(self):self.page.get_by_role('button',name='Choose without a photo',exact=True).first.click()
 def save(self,name='Friday dinner'):
  self.section().get_by_label('Look name',exact=True).fill(name);self.section().get_by_role('button',name='Save look',exact=True).click();expect(self.section().get_by_role('status')).to_contain_text('Look saved privately')
 def reuse(self,accept=True):
  self.page.once('dialog',lambda dialog:dialog.accept() if accept else dialog.dismiss());self.section().get_by_role('button',name=re.compile(r'^Use again\s*:')).first.click()
 def download(self,button):
  with self.page.expect_download() as event:self.section().get_by_role('button',name=button,exact=True).click()
  return Path(event.value.path()).read_text()
 def clean(self):self.assertEqual([],self.errors)

 def test_immutable_persistence_safe_export_rename_and_delete_confirmation(self):
  self.add('Owned rose');self.page.get_by_label('What are you getting ready for?',exact=True).fill('Dinner');self.choose();before=self.stored();self.save()
  saved=self.saved()['looks'][0];self.assertEqual(before['products'],saved['products']);self.assertEqual(before['rules'],saved['rules']);self.assertEqual('Dinner',saved['event']);self.assertEqual('constraints-only',saved['basis']);self.assertFalse(saved['sample']);self.assertFalse(saved['original'])
  self.page.get_by_role('button',name='Edit Owned rose',exact=True).click();self.page.get_by_label('Product name',exact=True).fill('Changed active rose');self.page.get_by_label('Approximate color',exact=True).fill('#112233');self.page.get_by_role('button',name='Save product changes',exact=True).click()
  self.assertEqual(saved,self.saved()['looks'][0]);expect(self.section().locator('.saved-look-detail')).to_contain_text('Owned rose');expect(self.section().locator('.saved-look-detail')).not_to_contain_text('Changed active rose')
  exported=json.loads(self.download('Download saved look'));self.assertEqual(saved,exported['look'])
  for secret in ['taskId','token','sourceHash','data:image',base.AWS]:self.assertNotIn(secret,json.dumps(exported))
  text=self.download('Save saved look as text');self.assertIn('Owned rose',text);self.assertIn('#a44357',text);self.assertIn('Dinner',text)
  self.page.reload();self.page.wait_for_load_state('networkidle');expect(self.section().get_by_role('button',name='Friday dinner',exact=True)).to_be_visible()
  self.section().get_by_role('button',name='Rename : Friday dinner',exact=True).click();self.section().get_by_label('New look name',exact=True).fill('Renamed dinner');self.section().get_by_role('button',name='Save name',exact=True).click();self.assertEqual({**saved,'name':'Renamed dinner'},self.saved()['looks'][0])
  self.page.once('dialog',lambda d:d.dismiss());self.section().get_by_role('button',name='Delete : Renamed dinner',exact=True).click();self.assertEqual(1,len(self.saved()['looks']))
  self.page.once('dialog',lambda d:d.accept());self.section().get_by_role('button',name='Delete : Renamed dinner',exact=True).click();self.assertEqual([],self.saved()['looks']);self.page.reload();self.page.wait_for_load_state('networkidle');expect(self.section()).to_contain_text('Your saved looks will appear here');self.assertEqual([],self.calls);self.clean()

 def test_loaded_preview_reuse_confirms_replaces_context_and_preserves_portrait_receipts(self):
  self.add('Owned rose');self.page.get_by_label('What are you getting ready for?',exact=True).fill('Saved occasion');self.photo();self.page.get_by_label(re.compile('I have permission')).check()
  self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).first.click();expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=15000);self.page.get_by_role('button',name='Choose this plan',exact=True).click();self.save('Historical preview')
  before=self.stored();self.assertEqual('loaded-preview',self.saved()['looks'][0]['basis']);self.page.get_by_role('button',name='Prefer right',exact=True).click();self.assertEqual(1,len(self.stored()['comparisons']))
  self.page.get_by_label('What are you getting ready for?',exact=True).fill('Active occasion');self.page.get_by_label('Minutes available',exact=True).fill('6');self.add('Unselected blush','blush',2);active=self.stored()
  self.reuse(False);self.assertEqual(active,self.stored());self.reuse();current=self.stored()
  self.assertEqual(before['products'],current['products']);self.assertEqual(before['rules'],current['rules']);self.assertEqual('Saved occasion',current['event']);self.assertEqual(before['sourceHash'],current['sourceHash']);self.assertEqual(before['tasks'],current['tasks']);self.assertEqual([],current['comparisons']);self.assertEqual('constraints-only',current['selectionBasis']);self.assertEqual('loaded-preview',self.saved()['looks'][0]['basis']);expect(self.page.get_by_role('img',name='Prepared original portrait',exact=True)).to_be_visible();self.assertEqual(['POST','GET'],self.calls);self.clean()

 def test_corrupt_bytes_export_and_deliberate_clear_recovery(self):
  raw=' {invalid saved-look bytes\n';self.page.evaluate('([k,v])=>localStorage.setItem(k,v)',[KEY,raw]);self.page.reload();self.page.wait_for_load_state('networkidle');expect(self.section()).to_contain_text('Original bytes are preserved');self.assertEqual(raw,self.download('Export original saved looks'));self.assertEqual(raw,self.page.evaluate('(k)=>localStorage.getItem(k)',KEY))
  self.page.get_by_role('button',name='Choose no added makeup',exact=True).click();self.section().get_by_label('Look name',exact=True).fill('Recovery');expect(self.section().get_by_role('button',name='Save look',exact=True)).to_be_disabled()
  self.page.once('dialog',lambda d:d.dismiss());self.section().get_by_role('button',name='Clear unreadable saved looks',exact=True).click();self.assertEqual(raw,self.page.evaluate('(k)=>localStorage.getItem(k)',KEY))
  self.page.once('dialog',lambda d:d.accept());self.section().get_by_role('button',name='Clear unreadable saved looks',exact=True).click();self.assertIsNone(self.page.evaluate('(k)=>localStorage.getItem(k)',KEY));self.save('Recovery');self.assertEqual(1,len(self.saved()['looks']));self.assertEqual([],self.calls);self.clean()

 def test_failed_write_is_visible_and_never_claimed_saved(self):
  self.add();self.choose();self.section().get_by_label('Look name',exact=True).fill('Unsaved look')
  self.page.evaluate("""()=>{const original=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='skinwise-private-saved-looks-v1')throw new DOMException('mock quota','QuotaExceededError');return original.call(this,k,v)}}""")
  self.section().get_by_role('button',name='Save look',exact=True).click();expect(self.section().get_by_role('alert')).to_contain_text('could not confirm the saved change');expect(self.section().get_by_role('button',name='Save look',exact=True)).to_be_disabled();self.assertIsNone(self.saved());expect(self.section().get_by_role('status')).to_have_count(0)
  self.page.reload();self.page.wait_for_load_state('networkidle');self.save('Recovered write');self.assertEqual(1,len(self.saved()['looks']));self.assertEqual([],self.calls);self.clean()

 def test_failed_write_clears_previous_success_status(self):
  self.add();self.choose();self.save('Confirmed earlier look');original=self.saved()
  self.page.evaluate("""()=>{const original=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='skinwise-private-saved-looks-v1')throw new DOMException('mock quota','QuotaExceededError');return original.call(this,k,v)}}""")
  self.section().get_by_label('Look name',exact=True).fill('Failed later look');self.section().get_by_role('button',name='Save look',exact=True).click();expect(self.section().get_by_role('alert')).to_contain_text('could not confirm the saved change');expect(self.section().get_by_role('status')).to_have_count(0);self.assertEqual(original,self.saved());self.assertEqual([],self.calls);self.clean()

 def test_capacity_80_character_names_mobile_and_print_isolation(self):
  self.page.set_viewport_size({'width':320,'height':844});self.add();self.choose();name='A very long saved look name '.ljust(80,'x');self.save(name);snapshot=self.saved()['looks'][0]
  self.assertEqual(80,len(snapshot['name']));expect(self.section().locator('.saved-look-detail')).to_contain_text(name);self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),320)
  self.page.evaluate("()=>{window.__savedPrintFlag=null;window.print=()=>window.__savedPrintFlag=document.body.dataset.skinwisePrintSavedLook}");self.section().get_by_role('button',name='Print saved look',exact=True).click();self.assertEqual('true',self.page.evaluate('window.__savedPrintFlag'));self.assertIsNone(self.page.evaluate('document.body.dataset.skinwisePrintSavedLook'))
  self.page.evaluate("()=>document.body.dataset.skinwisePrintSavedLook='true'");self.page.emulate_media(media='print');expect(self.section().locator('.saved-look-detail')).to_be_visible();expect(self.page.locator('.planner-handoff')).to_be_hidden();expect(self.section().get_by_role('button',name='Print saved look')).to_be_hidden();self.page.pdf(path=str(OUT/'saved-look-print.pdf'),format='A4',print_background=True);self.page.screenshot(path=str(OUT/'saved-look-print.png'),full_page=True);self.page.emulate_media(media='screen');self.page.evaluate('()=>delete document.body.dataset.skinwisePrintSavedLook')
  entries=[{**snapshot,'id':f'00000000-0000-4000-8000-{i:012d}','name':f'Look {i}'} for i in range(30)]
  self.page.evaluate('([k,v])=>localStorage.setItem(k,v)',[KEY,json.dumps({'version':1,'looks':entries})]);self.page.reload();self.page.wait_for_load_state('networkidle');expect(self.section()).to_contain_text('Library full');self.section().get_by_label('Look name',exact=True).fill('Must not evict');expect(self.section().get_by_role('button',name='Save look',exact=True)).to_be_disabled();self.assertEqual(entries,self.saved()['looks']);self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),320);self.assertEqual([],self.calls);self.clean()

 def test_original_fictional_choice_and_session_clear_preserve_library(self):
  self.page.get_by_role('button',name='Try the solver with a clearly fictional kit',exact=True).click();self.page.get_by_role('button',name='Choose no added makeup',exact=True).click();self.save('Fictional opt out');snapshot=self.saved()['looks'][0];self.assertTrue(snapshot['sample']);self.assertTrue(snapshot['original']);self.assertEqual([],snapshot['products']);self.assertEqual('original',snapshot['basis'])
  self.page.once('dialog',lambda d:d.accept());self.page.get_by_role('button',name='Clear session',exact=True).click();self.assertEqual(snapshot,self.saved()['looks'][0]);self.assertFalse(self.stored()['sample']);self.reuse();current=self.stored();self.assertTrue(current['sample']);self.assertEqual([],current['products']);self.assertEqual('original',current['selected']);self.assertEqual('original',current['selectionBasis']);self.assertEqual([],self.calls);self.clean()

 def test_reuse_disabled_during_preview_and_recovers_after_session_clear(self):
  self.add();self.choose();self.save('Busy guard');self.photo();self.page.get_by_label(re.compile('I have permission')).check();self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).first.click();expect(self.section().get_by_role('button',name='Use again : Busy guard',exact=True)).to_be_disabled();expect(self.section()).to_contain_text('Use again is paused')
  self.page.once('dialog',lambda d:d.accept());self.page.get_by_role('button',name='Clear session',exact=True).click();expect(self.section().get_by_role('button',name='Use again : Busy guard',exact=True)).to_be_enabled();self.reuse();self.assertEqual('constraints-only',self.stored()['selectionBasis']);self.assertEqual(['POST'],self.calls);self.clean()

if __name__=='__main__':unittest.main(verbosity=2)

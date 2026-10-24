"""Recovery regression gates. All API/images mocked; no paid calls.
PYTHONPATH=tests python -m unittest -v browser_planner_recovery
"""
import json
import unittest
from pathlib import Path
from playwright.sync_api import expect
import browser_planner as base
from browser_capture import png

class PlannerRecovery(unittest.TestCase):
 setUpClass=classmethod(base.PlannerAcceptance.setUpClass.__func__)
 tearDownClass=classmethod(base.PlannerAcceptance.tearDownClass.__func__)
 setUp=base.PlannerAcceptance.setUp
 tearDown=base.PlannerAcceptance.tearDown
 stored=base.PlannerAcceptance.stored
 add=base.PlannerAcceptance.add
 photo=base.PlannerAcceptance.photo
 ready=base.PlannerAcceptance.ready
 render=base.PlannerAcceptance.render
 export=base.PlannerAcceptance.export
 clean=base.PlannerAcceptance.clean
 def recovery(self):
  self.page.locator('.planner-recovery').evaluate('(element)=>element.open=true')
 def backup(self):
  self.recovery()
  with self.page.expect_download() as event:self.page.get_by_role('button',name='Save private recovery file',exact=True).click()
  return Path(event.value.path()).read_text()
 def restore(self,text):
  self.recovery()
  self.page.get_by_label('Restore a private recovery file',exact=True).set_input_files({'name':'private-recovery.json','mimeType':'application/json','buffer':text.encode()})
 def block_storage(self):
  self.page.evaluate('''key=>{const original=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k===key)throw new DOMException('Test quota exhausted','QuotaExceededError');return original.call(this,k,v)}}''',base.KEY)
 def test_invalid_session_preserved_byte_exact_and_exportable(self):
  raw='{ "event": 17, "tasks": [{"taskId":"mock-recoverable","token":"mock-private-receipt"}], "keep":"original bytes" }'
  self.page.evaluate('([key,raw])=>sessionStorage.setItem(key,raw)',[base.KEY,raw])
  self.page.reload();self.page.wait_for_load_state('networkidle')
  expect(self.page.get_by_role('alert')).to_contain_text('unreadable and has been preserved')
  self.add('A new local item')
  self.assertEqual(raw,self.page.evaluate('(key)=>sessionStorage.getItem(key)',base.KEY))
  with self.page.expect_download() as event:self.page.get_by_role('button',name='Export original session',exact=True).click()
  self.assertEqual(raw,Path(event.value.path()).read_text())
  self.assertEqual([],self.calls);self.clean()
 def test_write_exception_blocks_new_post_before_network(self):
  self.ready();self.block_storage()
  self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True).click()
  expect(self.page.get_by_role('alert')).to_contain_text('New paid previews are paused')
  self.assertEqual([],self.calls)
  backup=json.loads(self.backup());self.assertEqual('My rose lip',backup['products'][0]['name'])
  self.assertEqual([],backup['tasks']);self.clean()
 def test_private_backup_restore_get_only_and_public_export_isolated(self):
  self.ready();self.render();backup=self.backup();private=json.loads(backup)
  self.assertEqual(base.TOKEN,private['tasks'][0]['token'])
  self.assertNotIn(base.AWS,backup);self.assertNotIn('data:image',backup);self.assertNotIn('YOUCAM_API_KEY',backup)
  ordinary=json.dumps(self.export());self.assertNotIn(base.TOKEN,ordinary);self.assertNotIn('taskId',ordinary);self.assertNotIn('sourceHash',ordinary)
  self.page.once('dialog',lambda d:d.accept());self.page.get_by_role('button',name='Clear session',exact=True).click()
  self.assertEqual([],self.stored()['tasks'])
  self.restore(backup)
  expect(self.page.get_by_role('status')).to_contain_text('Recovery file restored')
  self.assertEqual(1,len(self.stored()['tasks']))
  expect(self.page.get_by_role('img',name='Prepared original portrait',exact=True)).to_have_count(0)
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=10000)
  self.assertEqual(['POST','GET','GET'],self.calls);self.clean()
 def test_invalid_import_preserves_current_model_and_receipt(self):
  self.ready();self.render();before=self.stored()
  self.restore(json.dumps({'products':before['products'],'rules':{'maxMinutes':0}}))
  expect(self.page.get_by_role('status')).to_contain_text('not a valid planner recovery file')
  self.assertEqual(before,self.stored())
  self.restore('PRIVATE_RECEIPT_MOCK_123')
  expect(self.page.get_by_role('status')).to_be_visible()
  self.assertNotIn('PRIVATE_RE',self.page.get_by_role('status').inner_text(),'Malformed recovery contents must not be echoed in the error UI')
  self.assertEqual(before,self.stored());self.assertEqual(['POST','GET'],self.calls);self.clean()
 def test_failure_after_started_task_keeps_private_receipt_and_allows_get(self):
  self.ready()
  def api(route):
   self.calls.append(route.request.method)
   if route.request.method=='POST':
    self.block_storage()
    route.fulfill(status=202,json={'status':'running','taskId':'mock-planner-task','token':base.TOKEN,'units':1})
   else:route.fulfill(json={'status':'success','url':base.AWS})
  self.page.route('**/api/makeup*',api)
  self.render()
  expect(self.page.get_by_role('alert')).to_contain_text('save a private recovery file')
  self.assertEqual([],self.stored()['tasks'])
  saved=json.loads(self.backup());self.assertEqual(base.TOKEN,saved['tasks'][0]['token'])
  self.page.get_by_role('button',name='Check / refresh existing task',exact=True).click()
  expect(self.page.get_by_role('button',name='Choose this plan',exact=True)).to_be_enabled(timeout=10000)
  self.assertEqual(['POST','GET','GET'],self.calls);self.clean()

if __name__=='__main__':unittest.main(verbosity=2)

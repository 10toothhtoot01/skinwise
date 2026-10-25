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

 def delay_photo_preparation(self):
  self.page.evaluate("""()=>{const original=HTMLCanvasElement.prototype.toBlob;
   HTMLCanvasElement.prototype.toBlob=function(callback,...args){original.call(this,blob=>{
    window.releasePlannerPhoto=()=>{HTMLCanvasElement.prototype.toBlob=original;callback(blob)};
    window.plannerPhotoPending=true;
   },...args)};
  }""")
  self.page.get_by_label('Portrait for visual rehearsal',exact=True).set_input_files({'name':'replacement.png','mimeType':'image/png','buffer':png(700,1024)})
  self.page.wait_for_function('window.plannerPhotoPending===true')
 def test_pending_photo_preparation_blocks_paid_start_and_recovers(self):
  self.ready();previous=self.stored()['sourceHash'];self.delay_photo_preparation()
  consent=self.page.get_by_label(base.re.compile('I have permission'))
  preview=self.page.get_by_role('button',name='Preview this option · 1 unit',exact=True)
  expect(consent).to_be_disabled()
  expect(consent).not_to_be_checked()
  expect(preview).to_be_disabled()
  # Programmatic events must not bypass pending-source ownership guards.
  consent.dispatch_event('click');preview.dispatch_event('click')
  self.assertEqual([],self.calls);self.assertEqual([],self.stored()['tasks'])
  self.page.evaluate('window.releasePlannerPhoto()')
  self.page.wait_for_function('([key,previous])=>JSON.parse(sessionStorage.getItem(key)).sourceHash!==previous',arg=[base.KEY,previous])
  expect(self.page.get_by_role('status')).to_contain_text('Prepared 700 × 1024 JPEG')
  expect(consent).to_be_enabled();expect(consent).not_to_be_checked()
  expect(self.page.get_by_label('Portrait for visual rehearsal',exact=True)).to_be_enabled()
  expect(preview).to_be_disabled();self.assertEqual([],self.calls)
  consent.check();self.render()
  self.assertEqual(['POST','GET'],self.calls);self.assertEqual(1,len(self.stored()['tasks']));self.clean()
 def test_clear_during_pending_photo_does_not_resurrect_source(self):
  self.ready();self.delay_photo_preparation()
  self.page.once('dialog',lambda dialog:dialog.accept())
  self.page.get_by_role('button',name='Clear session',exact=True).click()
  self.page.evaluate('window.releasePlannerPhoto()')
  # Flush the callback, blob/hash promises and React update opportunity.
  self.page.wait_for_timeout(150)
  self.assertIsNone(self.stored()['sourceHash']);self.assertEqual([],self.stored()['products'])
  self.assertEqual([],self.stored()['tasks'])
  expect(self.page.get_by_role('img',name='Prepared original portrait',exact=True)).to_have_count(0)
  expect(self.page.get_by_role('button',name='Checking preview…',exact=True)).to_have_count(0)
  expect(self.page.get_by_label('Portrait for visual rehearsal',exact=True)).to_be_enabled()
  self.assertEqual([],self.calls);self.clean()

 def delay_recovery_reads(self):
  self.recoveryProbeEmpty=self.stored()
  self.page.evaluate("""()=>{const original=Blob.prototype.text;window.plannerRecoveryReads={};
   Blob.prototype.text=function(){const file=this;return new Promise((resolve,reject)=>{
    window.plannerRecoveryReads[file.name]={resolve:()=>original.call(file).then(resolve,reject),reject:()=>reject(new Error('Mock stale read failure'))};
   })};
  }""")
 def queue_recovery(self,name,event='Recovered occasion',raw=None):
  self.recovery();model={**(self.stored() or self.recoveryProbeEmpty),'event':event}
  self.page.get_by_label('Restore a private recovery file',exact=True).set_input_files({'name':name,'mimeType':'application/json','buffer':(raw if raw is not None else json.dumps(model)).encode()})
  self.page.wait_for_function('(name)=>!!window.plannerRecoveryReads[name]',arg=name)
 def release_recovery(self,name,reject=False):
  self.page.evaluate('([name,operation])=>window.plannerRecoveryReads[name][operation]()',[name,'reject' if reject else 'resolve'])
  self.page.wait_for_timeout(100)
 def reset_for_recovery_probe(self):
  self.page.once('dialog',lambda dialog:dialog.accept())
  self.page.get_by_role('button',name='Clear session',exact=True).click()
 def test_latest_recovery_selection_wins_in_both_completion_orders(self):
  self.delay_recovery_reads()
  for index,order in enumerate([('earlier','latest'),('latest','earlier')]):
   with self.subTest(completion_order=order):
    if index:self.reset_for_recovery_probe()
    names={which:f'{which}-{index}.json' for which in order}
    self.queue_recovery(names['earlier'],'Earlier file');self.queue_recovery(names['latest'],'Latest file')
    for which in order:self.release_recovery(names[which])
    self.assertEqual('Latest file',self.stored()['event'])
    expect(self.page.locator('.planner-shell > .planner-message[role=status]')).to_contain_text('Recovery file restored')
  self.assertEqual([],self.calls);self.clean()
 def test_stale_recovery_read_errors_cannot_replace_newer_success_status(self):
  self.delay_recovery_reads()
  for index,reject in enumerate([False,True]):
   with self.subTest(rejected_read=reject):
    if index:self.reset_for_recovery_probe()
    old=f'old-{index}.json';new=f'new-{index}.json'
    self.queue_recovery(old,raw='malformed old recovery');self.queue_recovery(new,'Latest valid file')
    self.release_recovery(new)
    expect(self.page.locator('.planner-shell > .planner-message[role=status]')).to_contain_text('Recovery file restored')
    self.release_recovery(old,reject=reject)
    self.assertEqual('Latest valid file',self.stored()['event'])
    expect(self.page.locator('.planner-shell > .planner-message[role=status]')).to_contain_text('Recovery file restored')
  self.assertEqual([],self.calls);self.clean()
 def test_clear_invalidates_pending_recovery_reads_and_errors(self):
  self.delay_recovery_reads()
  for index,reject in enumerate([False,True]):
   with self.subTest(rejected_read=reject):
    name=f'cleared-{index}.json';self.queue_recovery(name)
    self.reset_for_recovery_probe();self.release_recovery(name,reject=reject)
    self.assertEqual(0,self.page.locator('.planner-kit li').count());self.assertEqual('',self.page.get_by_label('What are you getting ready for?',exact=True).input_value())
    expect(self.page.locator('.planner-shell > .planner-message[role=status]')).to_contain_text('Planning session cleared')
  self.assertEqual([],self.calls);self.clean()
 def test_local_edits_while_recovery_reads_require_current_state_confirmation(self):
  self.delay_recovery_reads()
  for index,kind in enumerate(['owned-product','occasion-only']):
   with self.subTest(local_edit=kind):
    if index:self.reset_for_recovery_probe()
    name=f'edited-{index}.json';self.queue_recovery(name)
    if kind=='owned-product':self.add('Newly entered owned lip')
    else:self.page.get_by_label('What are you getting ready for?',exact=True).fill('New local occasion')
    before=self.stored();dialogs=[]
    def dismiss(dialog):dialogs.append(dialog.message);dialog.dismiss()
    self.page.once('dialog',dismiss);self.release_recovery(name)
    self.page.remove_listener('dialog',dismiss)
    self.assertEqual(1,len(dialogs),'Pending restore must inspect current local edits before replacement')
    self.assertIn('Replace this planning session',dialogs[0])
    self.assertEqual(before,self.stored(),'Dismissing replacement must preserve the edited kit or occasion')
  self.assertEqual([],self.calls);self.clean()

if __name__=='__main__':unittest.main(verbosity=2)

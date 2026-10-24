"""Evidence workflow tests: every API/image response is mocked; no paid task.
PYTHONPATH=tests python -m unittest -v browser_evidence
"""
import json
import re
import unittest
from pathlib import Path
from playwright.sync_api import expect
import browser_acceptance as base
from browser_capture import png

RECEIPTS='skinwise-result-receipts-v1'
TOKEN='1799999999999.eyJwcm9maWxlIjoidmlzaWJsZSJ9.'+'a'*64
AWS='https://functional-fixtures.s3.amazonaws.com/'


def result(id='evidence-task', score=64):
    value=base.analysis(id,'youcam',[('pore','Pore appearance',score),('redness','Redness appearance',72)])
    value['regions']=[{'key':'pore','label':'Pore appearance','region':'left_cheek','score':58},
                      {'key':'pore','label':'Pore appearance','region':'nose','score':53}]
    return value


def visuals(prefix='one'):
    return {'originalUrl':AWS+prefix+'-original.png','items':[
        {'key':'pore','region':'whole','url':AWS+prefix+'-pore.png','kind':'overlay'},
        {'key':'pore','region':'left_cheek','url':AWS+prefix+'-cheek.png','kind':'overlay'},
        {'key':'redness','region':'whole','url':AWS+prefix+'-redness.png','kind':'mask'}]}


class EvidenceAcceptance(unittest.TestCase):
    setUpClass=classmethod(base.Acceptance.setUpClass.__func__)
    tearDownClass=classmethod(base.Acceptance.tearDownClass.__func__)
    setUp=base.Acceptance.setUp
    tearDown=base.Acceptance.tearDown
    open=base.Acceptance.open
    stored=base.Acceptance.stored
    click_nav=base.Acceptance.click_nav
    assert_clean=base.Acceptance.assert_clean
    live_setup=base.Acceptance.live_setup

    def seed(self,scans,receipts=None):
        self.open()
        self.page.evaluate('([key,scans,receiptKey,receipts])=>{localStorage.setItem(key,JSON.stringify({version:1,analyses:scans,experiment:null,checkins:[]}));localStorage.setItem(receiptKey,JSON.stringify(receipts));}',[base.KEY,scans,RECEIPTS,receipts or {}])
        self.page.reload();self.page.wait_for_load_state('networkidle')

    def inspect(self,index=0):
        self.click_nav('Progress')
        self.page.locator('.scan-row').nth(index).get_by_role('button',name='Inspect scan').click()
        return self.page.get_by_role('region',name='YouCam visual evidence')

    def mock_images(self,expired=False):
        self.page.route(AWS+'**',lambda route:route.fulfill(status=403 if expired else 200,content_type='application/xml' if expired else 'image/png',body=b'<Error>ExpiredToken</Error>' if expired else png(32,32)))

    def assert_private_export(self,data):
        text=json.dumps(data)
        self.assertNotIn('amazonaws.com',text)
        self.assertNotIn(TOKEN,text)
        self.assertNotIn('originalUrl',text)
        self.assertNotIn('visuals',text)
        self.assertNotIn('token',text)

    def test_returned_overlay_regions_and_visible_profile(self):
        self.mock_images();submitted=[]
        def handle(route):
            if route.request.method=='POST':
                submitted.append(route.request.post_data_buffer)
                route.fulfill(status=202,json={'status':'running','taskId':'evidence-task','token':TOKEN})
            else:route.fulfill(json={'status':'success','result':result(),'visuals':visuals()})
        self.page.route('**/api/analyze*',handle)
        self.live_setup();self.page.get_by_role('button',name='Analyse my skin').click()
        workspace=self.page.get_by_role('region',name='YouCam visual evidence')
        expect(workspace).to_be_visible(timeout=15000)
        self.assertEqual(1,len(submitted));self.assertIn(b'name="profile"',submitted[0]);self.assertIn(b'visible',submitted[0])
        image=workspace.get_by_role('img',name='YouCam overlay for Pore appearance, Whole')
        expect(image).to_have_attribute('src',AWS+'one-pore.png')
        expect(image).to_have_js_property('naturalWidth',32)
        workspace.get_by_role('group',name='Returned facial regions').get_by_role('button',name=re.compile('^Left cheek')).click()
        expect(workspace.get_by_role('img',name='YouCam overlay for Pore appearance, Left cheek')).to_have_attribute('src',AWS+'one-cheek.png')
        expect(workspace.get_by_text('Left cheek Pore appearance: 58/100',exact=True)).to_be_visible()
        workspace.get_by_role('group',name='Returned facial regions').get_by_role('button',name=re.compile('^Nose')).click()
        expect(workspace.get_by_text('No detection image is loaded for this concern and region.')).to_be_visible()
        expect(workspace.get_by_text('Nose Pore appearance: 53/100',exact=True)).to_be_visible()
        workspace.get_by_role('group',name='Returned facial regions').get_by_role('button',name=re.compile('^Whole face')).click()
        expect(workspace.get_by_text('Whole Pore appearance: 64/100',exact=True)).to_be_visible()
        expect(workspace.get_by_role('img',name='YouCam overlay for Pore appearance, Whole')).to_have_attribute('src',AWS+'one-pore.png')
        workspace.get_by_role('button',name='Redness appearance',exact=True).click()
        expect(workspace.get_by_role('img',name='YouCam mask for Redness appearance, Whole')).to_have_attribute('src',AWS+'one-redness.png')
        workspace.get_by_role('button',name='Texture appearance',exact=True).click()
        expect(workspace.get_by_text('No detection image is loaded for this concern and region.')).to_be_visible()
        expect(workspace.get_by_text('No score was returned for this concern and region.',exact=True)).to_be_visible()
        self.assert_private_export(self.stored())
        self.assertEqual(TOKEN,self.page.evaluate('(key)=>JSON.parse(localStorage.getItem(key))["evidence-task"].token',RECEIPTS))
        self.page.reload();self.page.wait_for_load_state('networkidle');workspace=self.inspect()
        expect(workspace.get_by_role('button',name='Refresh detection images')).to_be_enabled()
        expect(workspace.get_by_text('The provider input image is not loaded.')).to_be_visible()
        self.assertEqual(1,len(submitted))
        self.assert_clean()

    def test_three_part_receipt_reload_refresh_get_only(self):
        self.mock_images();calls=[]
        self.page.route('**/api/analyze*',lambda route:(calls.append(route.request.method),route.fulfill(json={'status':'success','result':result(),'visuals':visuals('refreshed')})))
        self.seed([result()],{'evidence-task':{'taskId':'evidence-task','token':TOKEN}})
        workspace=self.inspect()
        expect(workspace.get_by_text('The provider input image is not loaded.')).to_be_visible()
        self.assertEqual([],calls)
        workspace.get_by_role('button',name='Refresh detection images').click()
        expect(workspace.get_by_role('img',name='YouCam overlay for Pore appearance, Whole')).to_have_attribute('src',AWS+'refreshed-pore.png')
        self.assertEqual(['GET'],calls)
        self.page.reload();self.page.wait_for_load_state('networkidle');workspace=self.inspect()
        expect(workspace.get_by_text('The provider input image is not loaded.')).to_be_visible()
        expect(workspace.get_by_role('button',name='Refresh detection images')).to_be_enabled()
        self.assertEqual(['GET'],calls)
        self.assert_private_export(self.stored());self.assert_clean()

    def test_image_only_region_remains_inspectable_without_invented_score(self):
        self.page.set_viewport_size({'width':390,'height':844})
        self.mock_images();scan=result()
        scan['regions']=[{'key':'pore','label':'Pore appearance','region':'nose','score':53}]
        images=visuals()
        # Cheek has a real returned image but no valid UI score. Whole has an image only.
        scan['metrics']=[m for m in scan['metrics'] if m['key']!='pore']
        self.page.route('**/api/analyze*',lambda route:route.fulfill(json={'status':'success','result':scan,'visuals':images}))
        self.seed([scan],{'evidence-task':{'taskId':'evidence-task','token':TOKEN}})
        workspace=self.inspect()
        workspace.get_by_role('button',name='Refresh detection images').click()
        expect(workspace.get_by_role('img',name='YouCam overlay for Pore appearance, Whole')).to_have_attribute('src',AWS+'one-pore.png')
        group=workspace.get_by_role('group',name='Returned facial regions')
        group.get_by_role('button',name=re.compile('^Left cheek')).click()
        expect(workspace.get_by_role('img',name='YouCam overlay for Pore appearance, Left cheek')).to_have_attribute('src',AWS+'one-cheek.png')
        expect(workspace.get_by_text('No score was returned for this concern and region.',exact=True)).to_be_visible()
        group.get_by_role('button',name=re.compile('^Nose')).click()
        expect(workspace.get_by_text('Nose Pore appearance: 53/100',exact=True)).to_be_visible()
        group.get_by_role('button',name=re.compile('^Whole face')).click()
        expect(workspace.get_by_role('img',name='YouCam overlay for Pore appearance, Whole')).to_have_attribute('src',AWS+'one-pore.png')
        expect(workspace.get_by_text('No score was returned for this concern and region.',exact=True)).to_be_visible()
        self.assertEqual(1,len(self.analysis_requests));self.assert_clean()

    def test_expired_and_missing_images_do_not_invent_detection(self):
        self.mock_images(expired=True);calls=[]
        def handle(route):
            calls.append(route.request.method)
            if len(calls)==1:route.fulfill(json={'status':'success','result':result(),'visuals':visuals('expired')})
            else:route.fulfill(status=403,json={'error':'This completed task receipt has expired. No new analysis was started.','code':'INVALID_TASK'})
        self.page.route('**/api/analyze*',handle)
        self.seed([result()],{'evidence-task':{'taskId':'evidence-task','token':TOKEN}});workspace=self.inspect()
        workspace.get_by_role('button',name='Refresh detection images').click()
        expect(workspace.get_by_text('This temporary image could not load.',exact=False).first).to_be_visible()
        expect(workspace.get_by_role('img')).to_have_count(0)
        workspace.get_by_role('button',name='Refresh detection images').click()
        expect(workspace.get_by_role('status')).to_contain_text('receipt has expired')
        expect(workspace.get_by_text('Whole Pore appearance: 64/100',exact=True)).to_be_visible()
        self.assertEqual(['GET','GET'],calls);self.assert_private_export(self.stored());self.assert_clean()

    def test_historical_scan_review_persists_and_exports_without_private_state(self):
        self.seed([result('old-task',44),result('new-task',88)],{'old-task':{'taskId':'old-task','token':TOKEN}})
        workspace=self.inspect(index=1)
        expect(workspace.get_by_text('Whole Pore appearance: 44/100',exact=True)).to_be_visible()
        workspace.get_by_label('What did you notice in the marked area?').fill('My question was about the cheek, but the marking did not match it.')
        workspace.get_by_role('button',name='Does not match',exact=True).click()
        self.assertEqual('no',self.stored()['analyses'][0]['review']['match'])
        workspace.get_by_role('button',name='Matches my concern',exact=True).click()
        workspace.get_by_role('button',name='Save scan interpretation').click()
        self.page.reload();self.page.wait_for_load_state('networkidle');workspace=self.inspect(index=1)
        expect(workspace.get_by_role('button',name='Matches my concern',exact=True)).to_have_attribute('aria-pressed','true')
        expect(workspace.get_by_label('What did you notice in the marked area?')).to_have_value('My question was about the cheek, but the marking did not match it.')
        self.assertNotIn('review',self.stored()['analyses'][1])
        self.click_nav('My journal')
        with self.page.expect_download() as event:self.page.get_by_role('button',name='Export journal').click()
        exported=json.loads(Path(event.value.path()).read_text());self.assert_private_export(exported)
        self.assertEqual(self.stored(),exported);self.assertEqual('yes',exported['analyses'][0]['review']['match']);self.assert_clean()

    def test_delete_clears_receipts_and_ignores_late_image_refresh(self):
        held=[];self.mock_images()
        self.page.route('**/api/analyze*',lambda route:held.append(route))
        self.seed([result()],{'evidence-task':{'taskId':'evidence-task','token':TOKEN}});workspace=self.inspect()
        with self.page.expect_request(lambda req:'/api/analyze?' in req.url):workspace.get_by_role('button',name='Refresh detection images').click()
        self.page.wait_for_timeout(50);self.assertEqual(1,len(held))
        self.click_nav('My journal');self.page.get_by_role('button',name='Delete all data',exact=True).click()
        self.page.get_by_role('alertdialog').get_by_role('button',name='Delete all data',exact=True).click()
        held[0].fulfill(json={'status':'success','result':result(),'visuals':visuals('late')})
        self.page.wait_for_timeout(100)
        self.assertIsNone(self.page.evaluate('(key)=>localStorage.getItem(key)',RECEIPTS))
        self.assertIn(self.stored(),[None,base.journal([])])
        self.assertTrue(all('?' in url for url in self.analysis_requests),'No POST request should exist')
        self.page.reload();self.page.wait_for_load_state('networkidle');self.click_nav('Progress')
        expect(self.page.get_by_role('button',name='Inspect scan')).to_have_count(0)
        self.assert_clean()

    def test_hd_sd_cost_disclosure_before_submission(self):
        self.page.route('**/api/status',lambda route:route.fulfill(json={'configured':True}));self.open();self.click_nav('Skin check')
        for side,tier,units in [(1079,'SD','9'),(1080,'HD','12')]:
            self.page.get_by_label('Choose a skin photo').set_input_files({'name':'size-fixture.png','mimeType':'image/png','buffer':png(side,side)})
            expect(self.page.locator('.photo-preflight')).to_contain_text(f'{side} × {side}')
            expect(self.page.locator('.consent-row')).to_contain_text(f'{tier} · {units} API units')
        self.assertEqual([],self.analysis_requests);self.assert_clean()


if __name__=='__main__':unittest.main(verbosity=2)

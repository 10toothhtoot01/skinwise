"""Image decode, optional capture guidance and context: functional tests, no paid API.
SKINWISE_BASE_URL=http://127.0.0.1:5173 python tests/browser_capture.py
SDK mock assertions do not establish physical camera compatibility or capture quality.
"""
import base64
import io
import json
import unittest
from PIL import Image
from playwright.sync_api import expect
import browser_acceptance as base


def png(width=960, height=960):
    stream = io.BytesIO()
    Image.new('RGB', (width, height), (156, 128, 109)).save(stream, format='PNG')
    return stream.getvalue()


def context(**overrides):
    return {'workflow':'upload','width':960,'height':960,'setupLabel':'Phone at window','lighting':'daylight','camera':'front','unfiltered':'yes','guided':None, **overrides}


MOCK_SDK = '''() => {
 const handlers = new Map(); let counter=0;
 window.__camera = {config:null,opened:0,closed:0,emit:(name,data)=>{for (const e of [...handlers.values()]) if(e.name===name)e.fn(data);}};
 window.YMK = {
  init:config=>{window.__camera.config=config;},
  openCameraKit:()=>{window.__camera.opened++;window.__camera.emit('cameraOpened');},
  close:()=>{window.__camera.closed++;},
  addEventListener:(name,fn)=>{const id=++counter;handlers.set(id,{name,fn});return id;},
  removeEventListener:id=>handlers.delete(id)
 };
}'''


class CaptureAcceptance(unittest.TestCase):
    setUpClass = classmethod(base.Acceptance.setUpClass.__func__)
    tearDownClass = classmethod(base.Acceptance.tearDownClass.__func__)
    setUp = base.Acceptance.setUp
    tearDown = base.Acceptance.tearDown
    open = base.Acceptance.open
    stored = base.Acceptance.stored
    click_nav = base.Acceptance.click_nav
    assert_clean = base.Acceptance.assert_clean

    def capture_page(self):
        self.page.route('**/api/status', lambda route: route.fulfill(json={'configured':True}))
        self.open()
        self.click_nav('Skin check')

    def upload(self, buffer, mime='image/png'):
        self.page.get_by_label('Choose a skin photo').set_input_files({'name':'functional-fixture.png','mimeType':mime,'buffer':buffer})

    def assert_no_guided_photo(self):
        expect(self.page.locator('.photo-preflight')).not_to_be_visible()
        expect(self.page.get_by_alt_text('Your selected photo, shown only in this session')).not_to_be_visible()
        expect(self.page.get_by_role('button',name='Analyse my skin')).to_be_disabled()
        self.assertEqual([], self.analysis_requests)
        self.assertEqual([], self.stored()['analyses'])
        self.assert_clean()

    def test_decodable_image_bounds_and_upload_claim(self):
        self.capture_page()
        self.upload(png(479,960))
        expect(self.page.locator('.notice[role=status]')).to_contain_text('480-pixel minimum')
        self.assert_no_guided_photo()
        self.upload(png(480,960))
        expect(self.page.locator('.photo-preflight')).to_contain_text('480 × 960 pixels')
        expect(self.page.locator('.photo-preflight')).to_contain_text('Uploaded photo: resolution checked')
        expect(self.page.locator('.photo-preflight')).to_contain_text('have not been verified')
        self.assertEqual([], self.analysis_requests)
        self.page.get_by_role('button',name='Remove selected photo').click()
        self.upload(png(4097,480))
        expect(self.page.locator('.notice[role=status]')).to_contain_text('larger than 4096 pixels')
        self.assert_no_guided_photo()

    def test_decode_size_and_mime_fail_closed(self):
        self.capture_page()
        for content, mime, message in [(b'not-an-image','image/png','could not be decoded'),
            (png()+b'\0'*(8*1024*1024),'image/png','smaller than 8 MB'),
            (png(),'image/webp','JPEG or PNG')]:
            self.upload(content,mime)
            expect(self.page.locator('.notice[role=status]')).to_contain_text(message)
            self.assert_no_guided_photo()

    def test_sdk_download_failure_does_not_yield_photo(self):
        self.page.route('https://plugins-media.makeupar.com/**/sdk.js',lambda route:route.abort())
        self.capture_page()
        self.page.get_by_role('button',name='Open guided camera').click()
        expect(self.page.get_by_role('alert')).to_contain_text('could not download')
        self.assert_no_guided_photo()

    def start_mock(self):
        self.capture_page()
        self.page.evaluate(MOCK_SDK)
        self.page.get_by_role('button',name='Open guided camera').click()
        expect(self.page.get_by_label('Current capture checks')).to_be_visible()
        self.assertEqual(False,self.page.evaluate('window.__camera.config.disableCameraResolutionCheck'))
        self.assertEqual('1080p',self.page.evaluate('window.__camera.config.videoQuality'))

    def emit(self, event, data=None):
        self.page.evaluate('([event,data])=>window.__camera.emit(event,data)',[event,data])

    def test_sdk_permission_denial_and_resolution_failure(self):
        self.start_mock()
        self.emit('cameraFailed',{'code':'permission_denied'})
        expect(self.page.get_by_role('alert')).to_contain_text('access was denied')
        self.assert_no_guided_photo()
        self.page.get_by_role('button',name='Open guided camera').click()
        self.emit('unsupportedResolution')
        expect(self.page.get_by_role('alert')).to_contain_text('resolution requirement')
        self.assert_no_guided_photo()

    def test_sdk_quality_failure_cannot_claim_guided_capture(self):
        self.start_mock()
        for checks in [None,{'hasFace':False,'position':'good','frontal':'good','lighting':'good'},
                       {'hasFace':True,'position':'good','frontal':'bad','lighting':'good'},
                       {'hasFace':True,'position':'good','frontal':'good','lighting':'bad'}]:
            if checks is not None:
                self.emit('faceQualityChanged',checks)
            self.emit('faceDetectionCaptured',{'images':[{'image':'data:image/png;base64,'+base64.b64encode(png()).decode()}]})
            expect(self.page.get_by_role('alert')).to_contain_text('checks were not all available')
            self.assert_no_guided_photo()
            self.page.get_by_role('button',name='Open guided camera').click()

    def test_sdk_success_attaches_evidence_but_never_runs_analysis(self):
        self.start_mock()
        self.emit('faceQualityChanged',{'hasFace':True,'position':'good','frontal':'good','lighting':'ok'})
        self.emit('faceDetectionCaptured',{'images':[{'image':'data:image/png;base64,'+base64.b64encode(png()).decode()}]})
        expect(self.page.locator('.photo-preflight')).to_contain_text('960 × 960 pixels')
        expect(self.page.locator('.photo-preflight')).to_contain_text('Captured with YouCam’s guided checks')
        expect(self.page.locator('.photo-preflight')).to_contain_text('not a guarantee of score accuracy')
        expect(self.page.get_by_role('button',name='Analyse my skin')).to_be_disabled()
        self.assertEqual([],self.analysis_requests)
        self.assert_clean()

    def test_comparison_reports_context_limits(self):
        self.open()
        conditions=[(None,context(),'Capture context is missing'),
          (context(unfiltered='unknown'),context(),'Filter-free capture was not confirmed'),
          (context(),context(lighting='indoor'),'recorded camera or lighting setup changed'),
          (context(),context(setupLabel=''), 'capture setup is incomplete'),
          (context(),context(),None)]
        for before,after,message in conditions:
            first=base.analysis('first','youcam',[('moisture','Moisture appearance',60)])
            last=base.analysis('last','youcam',[('moisture','Moisture appearance',64)])
            if before is not None:first['capture']=before
            if after is not None:last['capture']=after
            self.page.evaluate('([key,value])=>localStorage.setItem(key,JSON.stringify(value))',[base.KEY,base.journal([first,last])])
            self.page.reload();self.page.wait_for_load_state('networkidle');self.click_nav('Progress')
            limit=self.page.locator('.comparison-chart .inline-note')
            if message:expect(limit).to_contain_text(message)
            else:
                expect(limit).to_have_count(0)
                expect(self.page.get_by_text('Descriptive score differences only.',exact=False)).to_contain_text('no reliable-change threshold')
            expect(self.page.locator('.comparison-row')).to_contain_text('+4')
        self.assert_clean()


    def test_capture_context_survives_pending_reload_and_export(self):
        calls={'post':0,'get':0}
        result=base.analysis('context-live','youcam',[('moisture','Moisture appearance',64)])
        def handle(route):
            method=route.request.method.lower();calls[method]+=1
            if method=='post':route.fulfill(status=202,json={'status':'running','taskId':'context-task','token':('1799999999999.'+'a'*64)})
            else:route.fulfill(json={'status':'success','result':result})
        self.page.route('**/api/analyze*',handle)
        self.capture_page();self.upload(png())
        expect(self.page.locator('.photo-preflight')).to_contain_text('960 × 960 pixels')
        self.page.locator('summary',has_text='Remember this setup').click()
        self.page.get_by_label('Device and setup name').fill('Phone at window')
        self.page.get_by_label('Light source').select_option('daylight')
        self.page.get_by_label('Camera used').select_option('front')
        self.page.get_by_label('No filter, beauty mode or makeup?').select_option('yes')
        self.page.get_by_role('checkbox').check()
        self.page.get_by_role('button',name='Analyse my skin').click()
        self.page.wait_for_function('localStorage.getItem("skinwise-pending-v1")!==null')
        self.page.reload();self.page.wait_for_load_state('networkidle');self.click_nav('Skin check')
        self.assertEqual({'post':1,'get':0},calls)
        self.page.get_by_role('button',name='Resume checking this analysis').click()
        expect(self.page.get_by_text('Live YouCam analysis',exact=False)).to_be_visible(timeout=15000)
        self.assertEqual(context(),self.stored()['analyses'][0]['capture'])
        self.assertEqual({'post':1,'get':1},calls)
        self.click_nav('My journal')
        with self.page.expect_download() as event:self.page.get_by_role('button',name='Export journal').click()
        exported=json.loads(base.Path(event.value.path()).read_text())
        self.assertEqual(context(),exported['analyses'][0]['capture'])
        self.assert_clean()


if __name__ == '__main__':
    unittest.main(verbosity=2)

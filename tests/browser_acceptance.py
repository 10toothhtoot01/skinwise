"""Functional browser acceptance; requests to analysis are mocked, never sent to YouCam.
SKINWISE_BASE_URL=http://127.0.0.1:5173 python tests/browser_acceptance.py
Requires Python Playwright and its Chromium browser.
"""
import base64
import json
import os
import re
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('SKINWISE_BASE_URL', 'http://127.0.0.1:5173')
KEY = 'skinwise-journal-v1'
EVIDENCE = Path(os.environ.get('SKINWISE_EVIDENCE_DIR', '../../work/qa-acceptance'))
EVIDENCE.mkdir(parents=True, exist_ok=True)


def analysis(id, source, metrics):
    return {'id': id, 'date': '2026-10-24T08:00:00.000Z', 'source': source,
            'metrics': [{'key': k, 'label': label, 'score': score} for k, label, score in metrics], 'concerns': []}


def journal(analyses):
    return {'version': 1, 'analyses': analyses, 'experiment': None, 'checkins': []}


class Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = sync_playwright().start()
        cls.browser = cls.p.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.p.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True)
        self.page = self.context.new_page()
        self.errors = []
        self.analysis_requests = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.on('request', lambda req: self.analysis_requests.append(req.url) if '/api/analyze' in req.url else None)

    def tearDown(self):
        self.page.screenshot(path=str(EVIDENCE / f'{self._testMethodName}.png'), full_page=True)
        (EVIDENCE / f'{self._testMethodName}.json').write_text(json.dumps({'uncaughtErrors': self.errors, 'analysisRequests': self.analysis_requests}, indent=2))
        self.context.close()

    def open(self, storage=None):
        if storage is not None:
            self.context.add_init_script(f'localStorage.setItem({json.dumps(KEY)}, {json.dumps(storage)});')
        self.page.goto(BASE)
        self.page.wait_for_load_state('networkidle')
        expect(self.page.get_by_role('heading', level=1)).to_be_visible()

    def stored(self):
        return self.page.evaluate('(key) => JSON.parse(localStorage.getItem(key))', KEY)

    def click_nav(self, label):
        self.page.get_by_role('navigation').get_by_role('button', name=re.compile('^' + re.escape(label) + r'(?:\s|$)')).click()

    def assert_analysis_with_capture(self, result):
        records = self.stored()['analyses']
        self.assertEqual(1, len(records))
        self.assertEqual(result, {k:v for k,v in records[0].items() if k != 'capture'})
        self.assertEqual({'workflow':'upload','width':480,'height':640,'setupLabel':'','lighting':'unknown','camera':'unknown','unfiltered':'unknown','guided':None}, records[0]['capture'])

    def assert_clean(self):
        self.assertEqual([], self.errors, 'Uncaught browser exceptions')

    def test_sample_journal_export_delete(self):
        self.open()
        self.page.get_by_role('button', name='Take a sample walkthrough').click()
        expect(self.page.get_by_text('Sample walkthrough · Fictional results for exploring the app')).to_be_visible()
        self.assertEqual([], self.analysis_requests)
        self.assertEqual('demo', self.stored()['analyses'][0]['source'])
        self.page.get_by_role('button', name='Plan one small change').click()
        self.page.get_by_label('One change to observe').fill('Keep my evening routine consistent')
        self.page.get_by_role('button', name='Save my intention').click()
        self.page.get_by_label('Your observation').fill('Feels comfortable after an ordinary day')
        self.page.get_by_role('button', name='4', exact=True).click()
        self.page.get_by_role('button', name='Save check-in').click()
        self.page.reload(); self.page.wait_for_load_state('networkidle')
        self.click_nav('My journal')
        expect(self.page.get_by_text('Keep my evening routine consistent', exact=True)).to_be_visible()
        expect(self.page.get_by_text('Feels comfortable after an ordinary day', exact=True)).to_be_visible()
        with self.page.expect_download() as download_event:
            self.page.get_by_role('button', name='Export journal').click()
        exported = json.loads(Path(download_event.value.path()).read_text())
        self.assertEqual(self.stored(), exported)
        self.assertEqual(4, exported['checkins'][0]['comfort'])
        self.assertNotIn('data:image', json.dumps(exported))
        self.page.get_by_role('button', name='Delete all data', exact=True).click()
        dialog = self.page.get_by_role('alertdialog')
        expect(dialog).to_be_visible()
        dialog.get_by_role('button', name='Keep my journal').click()
        self.assertEqual(1, len(self.stored()['checkins']))
        self.page.get_by_role('button', name='Delete all data', exact=True).click()
        dialog.get_by_role('button', name='Delete all data', exact=True).click()
        self.page.reload(); self.page.wait_for_load_state('networkidle')
        self.assertEqual(journal([]), self.stored())
        self.assert_clean()

    def test_sample_followup_comparison(self):
        self.open()
        self.page.get_by_role('button', name='Take a sample walkthrough').click()
        self.page.get_by_role('button', name='See your progress').click()
        self.page.get_by_role('button', name='Add a sample follow-up').click()
        self.page.get_by_role('button', name='See your progress').click()
        expect(self.page.get_by_text('Sample progress · Fictional observations, not measured improvement')).to_be_visible()
        expect(self.page.locator('.comparison-row')).to_have_count(4)
        self.assertEqual('+8scorepoints', re.sub(r'\s+', '', self.page.locator('.comparison-row').first.locator('strong').inner_text()))
        self.assertEqual([], self.analysis_requests)
        self.assert_clean()

    def test_source_and_metric_consistent_comparison(self):
        scans = [analysis('demo', 'demo', [('moisture','Hydration',99)]),
                 analysis('live1','youcam',[('moisture','Hydration',40),('texture','Texture',50)]),
                 analysis('live2','youcam',[('moisture','Hydration',45),('redness','Redness',60)])]
        for scan in scans[1:]:scan['method']={'provider':'youcam','endpointVersion':'2.1','tier':'SD','scoreKind':'ui_score','modelVersion':None}
        self.open(json.dumps(journal(scans)))
        self.click_nav('Progress')
        expect(self.page.get_by_text('2 live checks')).to_be_visible()
        expect(self.page.locator('.comparison-row')).to_have_count(1)
        expect(self.page.locator('.comparison-row').first).to_contain_text('Hydration')
        expect(self.page.locator('.comparison-row').first).to_contain_text('+5')
        self.assert_clean()

    def test_corrupt_storage(self):
        # Fresh context for each corrupt value; storage injected only before first load.
        for value in ['{broken', json.dumps({'version': 999}), json.dumps(journal([{}])), json.dumps({**journal([]), 'experiment': {'change': 7}, 'checkins': [None]})]:
            context = self.browser.new_context()
            context.add_init_script(f'localStorage.setItem({json.dumps(KEY)}, {json.dumps(value)});')
            page = context.new_page(); errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            page.goto(BASE); page.wait_for_load_state('networkidle')
            try:
                expect(page.get_by_role('heading', level=1)).to_be_visible()
                self.assertEqual(value, page.evaluate('(key) => localStorage.getItem(key)', KEY))
                expect(page.get_by_role('button', name='Export original')).to_be_visible()
                page.get_by_role('navigation').get_by_role('button', name='Progress', exact=True).click()
                expect(page.get_by_role('heading', level=1)).to_be_visible()
                self.assertEqual([], errors, f'Corrupt storage crashed the app: {value}')
            finally:
                context.close()

    def test_mobile_views_and_keyboard(self):
        self.open()
        for width in [390, 320]:
            self.page.set_viewport_size({'width': width, 'height': 844})
            for label in ['Overview', 'Skin check', 'My journal', 'Progress']:
                self.click_nav(label)
                self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth > innerWidth'), f'Overflow in {label} at {width}px')
            self.page.screenshot(path=str(EVIDENCE / f'mobile-{width}.png'), full_page=True)
        self.page.reload(); self.page.wait_for_load_state('networkidle')
        self.page.keyboard.press('Tab')
        expect(self.page.get_by_role('link', name='Skip to content')).to_be_focused()
        self.page.keyboard.press('Enter')
        self.click_nav('My journal')
        self.page.get_by_role('button', name='Delete all data', exact=True).click()
        dialog = self.page.get_by_role('alertdialog')
        expect(dialog.get_by_role('button', name='Keep my journal')).to_be_focused()
        self.page.keyboard.press('Shift+Tab')
        self.assertTrue(self.page.evaluate('document.activeElement.closest("[role=alertdialog]") !== null'), 'Modal focus escapes to the background')
        self.page.keyboard.press('Escape')
        expect(dialog).not_to_be_visible()
        self.assert_clean()

    def live_setup(self):
        self.page.route('**/api/status', lambda route: route.fulfill(json={'configured': True}))
        self.open()
        self.click_nav('Skin check')
        png = self.page.evaluate('''() => {const c=document.createElement('canvas');c.width=480;c.height=640;return c.toDataURL('image/png').split(',')[1];}''')
        self.page.get_by_label('Choose a skin photo').set_input_files({'name':'synthetic-test.png', 'mimeType':'image/png', 'buffer':base64.b64decode(png)})
        expect(self.page.get_by_role('button', name='Analyse my skin')).to_be_disabled()
        self.page.get_by_role('checkbox').check()
        expect(self.page.get_by_role('button', name='Analyse my skin')).to_be_enabled()

    def test_provider_error_does_not_create_sample(self):
        self.page.route('**/api/analyze', lambda route: route.fulfill(status=429, json={'error':'The analysis service is busy. Wait a minute before trying again.', 'code':'PROVIDER_BUSY'}))
        self.live_setup()
        self.page.get_by_role('button', name='Analyse my skin').click()
        expect(self.page.locator('.notice[role=status]')).to_contain_text('Wait a minute before trying again')
        expect(self.page.get_by_role('button', name='Analyse my skin')).to_be_enabled()
        self.assertEqual([], self.stored()['analyses'])
        self.assert_clean()

    def test_async_provider_success(self):
        result = analysis('mock-live','youcam',[('moisture','Hydration',61),('texture','Texture',74)])
        def handle(route):
            if route.request.method == 'POST':
                route.fulfill(status=202, json={'status':'running','taskId':'mock-task','token':('1799999999999.' + 'a'*64),'pollingInterval':1,'units':12})
            else:
                route.fulfill(json={'status':'success','result':result})
        self.page.route('**/api/analyze*', handle)
        self.live_setup()
        self.page.get_by_role('button', name='Analyse my skin').click()
        expect(self.page.get_by_text('Live YouCam analysis', exact=False)).to_be_visible(timeout=15000)
        self.assert_analysis_with_capture(result)
        self.assert_clean()


    def test_single_checkin_delete_confirmation(self):
        data = journal([])
        data['checkins'] = [{'id':'note1','date':'2026-10-24T08:00:00.000Z','note':'Keep until confirmed','comfort':3}]
        self.open(json.dumps(data))
        self.click_nav('My journal')
        self.page.once('dialog', lambda dialog: dialog.dismiss())
        self.page.get_by_role('button', name=re.compile('^Delete check-in')).click()
        expect(self.page.get_by_text('Keep until confirmed', exact=True)).to_be_visible()
        self.page.once('dialog', lambda dialog: dialog.accept())
        self.page.get_by_role('button', name=re.compile('^Delete check-in')).click()
        expect(self.page.get_by_text('Keep until confirmed', exact=True)).not_to_be_visible()
        self.assertEqual([], self.stored()['checkins'])
        self.assert_clean()

    def test_pending_analysis_refresh_resumes_without_second_upload(self):
        result = analysis('resumed-live','youcam',[('moisture','Hydration',62)])
        calls = {'post':0, 'get':0}
        def handle(route):
            method = route.request.method.lower()
            calls[method] += 1
            if method == 'post':
                route.fulfill(status=202, json={'status':'running','taskId':'resumable-task','token':('1799999999999.' + 'a'*64),'units':12})
            else:
                route.fulfill(json={'status':'success','result':result})
        self.page.route('**/api/analyze*', handle)
        self.live_setup()
        self.page.get_by_role('button', name='Analyse my skin').click()
        self.page.wait_for_function('localStorage.getItem("skinwise-pending-v1") !== null')
        self.page.reload(); self.page.wait_for_load_state('networkidle')
        self.click_nav('Skin check')
        expect(self.page.get_by_role('button', name='Resume checking this analysis')).to_be_enabled()
        expect(self.page.get_by_role('checkbox')).not_to_be_checked()
        self.assertEqual({'post':1,'get':0}, calls)
        self.page.get_by_role('button', name='Resume checking this analysis').click()
        expect(self.page.get_by_text('Live YouCam analysis', exact=False)).to_be_visible(timeout=15000)
        self.assertEqual({'post':1,'get':1}, calls)
        self.assert_analysis_with_capture(result)
        self.assert_clean()

    def test_terminal_analysis_failure_allows_fresh_photo(self):
        def handle(route):
            if route.request.method == 'POST':
                route.fulfill(status=202, json={'status':'running','taskId':'failed-task','token':('1799999999999.' + 'a'*64),'units':12})
            else:
                route.fulfill(status=422, json={'error':'Retake a single-person, front-facing photo in even lighting.', 'code':'ANALYSIS_FAILED'})
        self.page.route('**/api/analyze*', handle)
        self.live_setup()
        self.page.get_by_role('button', name='Analyse my skin').click()
        expect(self.page.locator('.notice[role=status]')).to_contain_text('Retake a single-person', timeout=15000)
        expect(self.page.get_by_role('button', name='Analyse my skin')).to_be_visible()
        expect(self.page.get_by_role('button', name='Resume checking this analysis')).not_to_be_visible()
        self.assertEqual([], self.stored()['analyses'])
        self.assert_clean()


    def test_late_analysis_result_cannot_restore_deleted_data(self):
        held = []
        result = analysis('late-live','youcam',[('moisture','Hydration',63)])
        def handle(route):
            if route.request.method == 'POST':
                route.fulfill(status=202, json={'status':'running','taskId':'late-task','token':('1799999999999.' + 'a'*64),'units':12})
            else:
                held.append(route)
        self.page.route('**/api/analyze*', handle)
        self.live_setup()
        with self.page.expect_request(lambda request: '/api/analyze?' in request.url, timeout=15000):
            self.page.get_by_role('button', name='Analyse my skin').click()
        self.page.wait_for_timeout(50)
        self.assertEqual(1, len(held), 'Polling request should be in flight before clearing data')
        self.click_nav('My journal')
        self.page.get_by_role('button', name='Delete all data', exact=True).click()
        self.page.get_by_role('alertdialog').get_by_role('button', name='Delete all data', exact=True).click()
        held[0].fulfill(json={'status':'success','result':result})
        self.page.wait_for_timeout(100)
        self.assertIn(self.stored(), [None, journal([])])
        expect(self.page.get_by_role('heading', level=1)).to_have_text('A good day to know your skin.')
        self.assertIsNone(self.page.evaluate('localStorage.getItem("skinwise-pending-v1")'))
        self.assert_clean()


    def test_accuracy_limits_and_overview_promises(self):
        self.open()
        overview = self.page.locator('main').inner_text().lower()
        for promise in ['find what works for your skin', 'clinically proven', 'accurately measures', 'proven improvement']:
            self.assertNotIn(promise, overview)
        self.page.get_by_role('button', name='Take a sample walkthrough').click()
        summary = self.page.locator('summary', has_text='What can these scores tell you?')
        expect(summary).to_be_visible()
        summary.focus()
        self.page.keyboard.press('Enter')
        details = self.page.locator('details.accuracy-note')
        expect(details).to_have_attribute('open', '')
        expect(details).to_contain_text('A score of 72 is not 72% hydration, 72% healthy skin, or 72% confidence.')
        expect(details).to_contain_text('not measured with a skin sensor')
        expect(details).to_contain_text('Skinwise has not validated real-world accuracy or repeatability for this API configuration.')
        expect(details).to_contain_text('They do not establish that a few score points mean your skin improved or a product worked.')
        self.assertEqual([], self.analysis_requests)
        self.assert_clean()

    def test_checkin_preserves_intention_after_experiment_closes(self):
        self.open()
        self.click_nav('My journal')
        intention = 'Keep the evening routine consistent for observations'
        self.page.get_by_label('One change to observe').fill(intention)
        self.page.get_by_role('button', name='Save my intention').click()
        self.page.get_by_label('Your observation').fill('Comfortable; same device and window light')
        self.page.get_by_role('button', name='Save check-in').click()
        self.page.once('dialog', lambda dialog: dialog.accept())
        self.page.get_by_role('button', name='Close this experiment').click()
        self.page.get_by_label('Your observation').fill('Later note without an active intention')
        self.page.get_by_role('button', name='Save check-in').click()
        self.page.reload(); self.page.wait_for_load_state('networkidle')
        self.click_nav('My journal')
        expect(self.page.get_by_text('Recorded during: ' + intention, exact=True)).to_be_visible()
        data = self.stored()
        self.assertIsNone(data['experiment'])
        self.assertEqual(intention, data['checkins'][0]['intention'])
        self.assertNotIn('intention', data['checkins'][1])
        with self.page.expect_download() as event:
            self.page.get_by_role('button', name='Export journal').click()
        exported = json.loads(Path(event.value.path()).read_text())
        self.assertEqual(data, exported)
        self.assert_clean()

    def test_optional_analysis_method_survives_reload_and_export(self):
        record = analysis('method-live','youcam',[('moisture','Moisture appearance',72)])
        record['method'] = {'provider':'youcam','endpointVersion':'v2.1','tier':'SD','scoreKind':'ui_score','modelVersion':None}
        self.open(json.dumps(journal([record])))
        self.page.reload(); self.page.wait_for_load_state('networkidle')
        self.click_nav('My journal')
        with self.page.expect_download() as event:
            self.page.get_by_role('button', name='Export journal').click()
        exported = json.loads(Path(event.value.path()).read_text())
        self.assertEqual(record, exported['analyses'][0])
        self.assertEqual(record['method'], self.stored()['analyses'][0]['method'])
        self.assert_clean()


    def test_missing_live_method_withholds_numeric_delta(self):
        method={'provider':'youcam','endpointVersion':'2.1','tier':'HD','scoreKind':'ui_score','modelVersion':None}
        self.open()
        for before,after in [(None,method),(method,None),(None,None)]:
            first=analysis('unknown-first','youcam',[('pore','Pore appearance',50)])
            last=analysis('unknown-last','youcam',[('pore','Pore appearance',75)])
            if before is not None:first['method']=before
            if after is not None:last['method']=after
            self.page.evaluate('([key,value])=>localStorage.setItem(key,JSON.stringify(value))',[KEY,journal([first,last])])
            self.page.reload();self.page.wait_for_load_state('networkidle');self.click_nav('Progress')
            expect(self.page.locator('.comparison-chart .inline-note').first).to_contain_text('Analysis method metadata is missing')
            expect(self.page.locator('.comparison-row')).to_contain_text('Not comparable')
            self.assertNotIn('+25',self.page.locator('.comparison-row').inner_text())
            self.assertEqual([50,75],[a['metrics'][0]['score'] for a in self.stored()['analyses']])
        self.assertEqual([],self.analysis_requests)
        self.assert_clean()

    def test_known_method_change_withholds_numeric_delta(self):
        first=analysis('method-first','youcam',[('moisture','Moisture appearance',60)])
        last=analysis('method-last','youcam',[('moisture','Moisture appearance',65)])
        method={'provider':'youcam','endpointVersion':'v2.1','tier':'SD','scoreKind':'ui_score','modelVersion':None}
        first['method']=method
        last['method']={**method,'tier':'HD'}
        self.open(json.dumps(journal([first,last])))
        self.click_nav('Progress')
        expect(self.page.get_by_text('Not comparable',exact=False)).to_be_visible()
        self.assertNotIn('+5',self.page.locator('main').inner_text())
        expect(self.page.locator('.comparison-row')).to_have_count(1)
        expect(self.page.locator('.comparison-row strong')).to_contain_text('—')
        self.assert_clean()


if __name__ == '__main__':
    unittest.main(verbosity=2)

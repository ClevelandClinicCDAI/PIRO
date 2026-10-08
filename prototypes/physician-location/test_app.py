"""Contract tests for event identity, history, timezone boundaries and authentication."""
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
import app as module


class PresenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        module.DB_PATH = self.tmp.name + '/test.sqlite3'
        os.environ['PRESENCE_PROTOTYPE_ENABLED'] = 'true'
        os.environ['PRESENCE_INGEST_TOKEN'] = 'test-only'
        self.client = TestClient(module.app)
        self.client.__enter__()
        self.headers = {'X-Presence-Token':'test-only'}

    def tearDown(self):
        self.client.__exit__(None,None,None)
        self.tmp.cleanup()

    def event(self, **kwargs):
        return dict(event_id=str(uuid4()), physician_id=module.PHYSICIANS[0]['physician_id'], username=module.PHYSICIANS[0]['username'],
                    device_id='DEMO-MAIN-01', occurred_at='2026-09-29T16:00:00Z', synthetic=True,
                    session_type='console', network_context='onsite', **kwargs)

    def post(self, event):
        return self.client.post('/work-location/events', json=event, headers=self.headers)

    def person(self, day='2026-09-29'):
        return self.client.get('/work-location/physicians',params={'day':day}).json()['physicians'][0]

    def test_auth_and_synthetic_identity(self):
        event=self.event()
        self.assertEqual(self.client.post('/work-location/events',json=event).status_code,401)
        event['synthetic']=False
        self.assertEqual(self.post(event).status_code,422)
        event['synthetic']=True; event['username']='REAL\\someone'
        self.assertEqual(self.post(event).status_code,422)
        self.assertEqual(len(self.person()['events']),0)

    def test_deduplicate_but_retain_distinct_logins_and_reject_id_reuse(self):
        event=self.event()
        self.assertFalse(self.post(event).json()['duplicate'])
        self.assertTrue(self.post(event).json()['duplicate'])
        event['network_context']='offsite'
        self.assertEqual(self.post(event).status_code,409)
        event['event_id']=str(uuid4())
        self.assertEqual(self.post(event).status_code,200)
        self.assertEqual(len(self.person()['events']),2)

    def test_delayed_delivery_and_remote_session(self):
        newer=self.event(); newer['network_context']='offsite'
        self.post(newer)
        older=self.event(); older['occurred_at']='2026-09-29T15:00:00Z'
        self.post(older)
        self.assertEqual(self.person()['status'],'Remote')
        remote=self.event(); remote['session_type']='remote'; remote['occurred_at']='2026-09-29T17:00:00Z'
        self.post(remote)
        self.assertEqual(self.person()['status'],'Unknown')
        self.assertEqual(len(self.person()['events']),3)

    def test_timezone_and_timestamp_validation(self):
        event=self.event(); event['occurred_at']='2026-09-30T02:00:00Z'
        self.post(event)
        self.assertEqual(len(self.person()['events']),1)
        self.assertEqual(self.person('2026-09-30')['status'],'No Activity Today')
        event['event_id']=str(uuid4()); event['occurred_at']='2026-09-29T12:00:00'
        self.assertEqual(self.post(event).status_code,422)
        event['occurred_at']=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()
        self.assertEqual(self.post(event).status_code,422)

if __name__=='__main__':
    unittest.main()

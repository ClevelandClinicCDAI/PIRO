"""Portable equivalent of the PowerShell sender for testing this Mac/Docker setup."""
import argparse
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from uuid import uuid4


def request(base, path, token=None, payload=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Presence-Token"] = token
    req = urllib.request.Request(base.rstrip('/') + path, headers=headers,
                                 data=json.dumps(payload).encode() if payload else None)
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://localhost:8002')
    parser.add_argument('--physician', type=int, choices=range(1,26), default=1)
    parser.add_argument('--location', choices=['office','remote','unknown','remote-session'], default='office')
    parser.add_argument('--seed', action='store_true', help='Add illustrative logins for 19 of 25 synthetic physicians')
    args = parser.parse_args()
    if urlparse(args.base_url).hostname not in ('localhost','127.0.0.1','::1'):
        parser.error('Synthetic sender only supports loopback destinations')
    token = os.environ.get('PRESENCE_INGEST_TOKEN')
    if not token:
        parser.error('Set PRESENCE_INGEST_TOKEN')
    roster = request(args.base_url, '/work-location/physicians')['physicians']
    now = datetime.now(timezone.utc)
    people = roster if args.seed else [roster[args.physician-1]]
    for index, person in enumerate(people):
        if args.seed and index % 4 == 2:
            continue
        location = ('office' if index % 2 == 0 else 'remote') if args.seed else args.location
        payload = dict(event_id=str(uuid4()), physician_id=person['physician_id'], username=person['username'],
                       occurred_at=(now-timedelta(minutes=index+5) if args.seed else now).isoformat(),
                       event_type='logon', synthetic=True,
                       device_id='DEMO-LAPTOP-01' if location=='remote' else 'DEMO-MAIN-01',
                       session_type='remote' if location=='remote-session' else 'console',
                       network_context='offsite' if location=='remote' else 'unknown' if location=='unknown' else 'onsite')
        result = request(args.base_url, '/work-location/events', token, payload)
        print(f"{person['name']}: {location}; accepted={result['accepted']}, duplicate={result['duplicate']}")


if __name__ == '__main__':
    main()

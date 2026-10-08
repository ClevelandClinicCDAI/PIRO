"""Portable equivalent of the PowerShell sender for testing this Mac/Docker setup."""
import argparse
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
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
    devices = json.loads(Path(__file__).with_name('buildings.json').read_text())
    device_ids = list(devices)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://localhost:8002')
    parser.add_argument('--physician', type=int, default=1, help='One-based position in the current prototype roster')
    parser.add_argument('--location', choices=['office','remote','unknown','remote-session'], default='office')
    parser.add_argument('--building', choices=list(devices.values()), help='Building for an individual office login; defaults to cycling through the building catalog by physician')
    parser.add_argument('--seed', action='store_true', help='Add simulated logins, leaving every fourth roster member without a new event')
    args = parser.parse_args()
    if args.building and (args.seed or args.location != 'office'):
        parser.error('--building requires an individual --location office login')
    if urlparse(args.base_url).hostname not in ('localhost','127.0.0.1','::1'):
        parser.error('Synthetic sender only supports loopback destinations')
    token = os.environ.get('PRESENCE_INGEST_TOKEN')
    if not token:
        parser.error('Set PRESENCE_INGEST_TOKEN')
    roster = request(args.base_url, '/work-location/physicians')['physicians']
    if not args.seed and not 1 <= args.physician <= len(roster):
        parser.error(f'--physician must be between 1 and {len(roster)}')
    now = datetime.now(timezone.utc)
    people = [person for index, person in enumerate(roster) if index % 4 != 2] if args.seed else [roster[args.physician-1]]
    for index, person in enumerate(people):
        location = ('office' if index < len(device_ids) else 'remote') if args.seed else args.location
        device_id = device_ids[(index if args.seed else args.physician-1) % len(device_ids)]
        if args.building:
            device_id = next(device for device, building in devices.items() if building == args.building)
        payload = dict(event_id=str(uuid4()), physician_id=person['physician_id'], username=person['username'],
                       occurred_at=(now-timedelta(minutes=index+5) if args.seed else now).isoformat(),
                       event_type='logon', synthetic=True,
                       device_id='DEMO-LAPTOP-01' if location=='remote' else device_id,
                       session_type='remote' if location=='remote-session' else 'console',
                       network_context='offsite' if location=='remote' else 'unknown' if location=='unknown' else 'onsite')
        result = request(args.base_url, '/work-location/events', token, payload)
        site = devices[device_id] if location == 'office' else location
        print(f"{person['name']}: {site}; accepted={result['accepted']}, duplicate={result['duplicate']}")


if __name__ == '__main__':
    main()

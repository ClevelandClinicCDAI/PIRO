# Physician location — local synthetic prototype

This prototype adds `/physician-location` to the PIRO Angular app. A separate FastAPI container stores events in a persistent SQLite Docker volume. It **does not import PIRO's shared database connection or change shared SQL/Solr data**. All 25 physicians are fictional. No identity or location is collected from this computer.

The prototype is deliberately separate from production authentication and SQL Server deployment. Dashboard reads are public synthetic data; event writes require a random local token, and their published port is loopback-only. Never deploy this setup for real staff data. The normal PIRO API container is left running with its existing configuration.

## Start

From the repository root, create a local token once (the file is ignored by Git):

```sh
python3 -c 'import pathlib,secrets; p=pathlib.Path("prototypes/physician-location/.env.local"); p.touch(exist_ok=False); p.chmod(0o600); p.write_text("PRESENCE_INGEST_TOKEN="+secrets.token_hex(32)+"\n")'
```

If `.env.local` already exists, reuse it. The prototype reuses the existing `piro-api` image's Python dependencies. Build that image first if it is absent.

```sh
npm ci --prefix piro-ui
npm run build:prod --prefix piro-ui
docker compose --env-file prototypes/physician-location/.env.local -f docker-compose.yml -f docker-compose.override.yml -f prototypes/physician-location/compose.yml up -d --no-deps presence-api ui
```

The existing nginx UI container serves the locally compiled Angular bundle through a read-only mount. Rebuild Angular after UI edits; no image rebuild is required for this prototype.

Open <http://localhost:8080/physician-location>. The UI refreshes every five seconds. Use Refresh for an immediate read. Specialty/region counts reflect the full roster, while the result count reflects active filters. Save/Load keeps filters in this browser. Expand a physician to view all events for the selected Eastern-time date.

## Send synthetic events from this Mac

```sh
set -a
. prototypes/physician-location/.env.local
set +a
python3 prototypes/physician-location/send_synthetic_login.py --seed
python3 prototypes/physician-location/send_synthetic_login.py --physician 1 --location remote
python3 prototypes/physician-location/send_synthetic_login.py --physician 1 --location office
python3 prototypes/physician-location/send_synthetic_login.py --physician 1 --location remote-session
```

Each invocation produces a distinct login. Seeding adds 19 logins and leaves six physicians without events; it is additive, not a reset. The prototype displays the latest event by occurrence time, even if older events arrive later. A remote-desktop session is classified Unknown; an off-site console event is Remote, never assumed to be a home address.

## PowerShell dummy sender

On a Windows computer running this local stack (or PowerShell on this Mac), provide the same local token in `PRESENCE_INGEST_TOKEN`, then run:

```powershell
./prototypes/physician-location/send-synthetic-login.ps1 -Physician 1 -Location Remote
./prototypes/physician-location/send-synthetic-login.ps1 -Physician 1 -Location Office
```

The sender contains no credentials and never reads the real Windows identity, hostname or network. Both senders intentionally accept only loopback destinations. Windows `localhost` means that Windows machine, not this Mac. For testing on this Mac, the Python sender submits the same JSON contract.

For an exact retry test, retain both values and invoke the command twice with unchanged parameters:

```powershell
$event = [Guid]::NewGuid()
$time = [DateTimeOffset]::UtcNow
./prototypes/physician-location/send-synthetic-login.ps1 -Physician 1 -Location Office -EventId $event -OccurredAt $time
./prototypes/physician-location/send-synthetic-login.ps1 -Physician 1 -Location Office -EventId $event -OccurredAt $time
```

The second request returns `duplicate: true`. Reusing an event ID with a changed payload returns HTTP 409. Separate events are always retained.

## API contract

- `GET /work-location/physicians?day=YYYY-MM-DD` — synthetic roster and selected-day history; day defaults to America/New_York.
- `POST /work-location/events` — requires `X-Presence-Token` on the loopback port 8002.
- Required payload: `event_id` (UUID), `physician_id`, `username`, `device_id`, timezone-aware `occurred_at`, `synthetic: true`.
- Optional enums: `event_type: logon`, `session_type: console|remote`, `network_context: onsite|offsite|unknown`.
- Only the predefined synthetic roster is accepted. Device names must start with `DEMO-`. The server maps known devices to sites; unrecognized on-site devices yield Unknown.
- Event time and receipt time are both retained. More than five minutes of future clock skew is rejected.

## Tests

```sh
docker compose --env-file prototypes/physician-location/.env.local -f docker-compose.yml -f docker-compose.override.yml -f prototypes/physician-location/compose.yml run --rm --no-deps presence-api python -m unittest -v test_app
```

Tests cover credential rejection, synthetic identity enforcement, duplicate/conflicting event IDs, multiple logins, delayed delivery, remote-session ambiguity, date boundaries, and timestamp validation.

## Limits and next steps

This is a login-observation prototype, not a live attendance system. It does not infer physical presence, automatically expire today's observations, or resolve simultaneous sessions across multiple devices. It shows Unknown for ambiguous remote sessions. The UI says No Activity Today for an empty selected date, including historical dates. No production Windows deployment, certificate authentication, event spool/retry agent, directory integration, or real physician roster has been installed.

Before production, integrate role-protected reads, trustworthy session identity, managed device authentication, server-side IT location mappings, retention, and a SQL Server migration. The local token is only a prototype credential, not a recommended Windows rollout mechanism.

To return the UI to its usual nginx configuration, recreate only the UI using the original two Compose files. Stop `presence-api` separately if desired; keep its volume to retain test history. No database reset is necessary.

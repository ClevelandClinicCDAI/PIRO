# Physician location — local synthetic prototype

This prototype adds `/physician-location` to the PIRO Angular app. A separate FastAPI container stores simulated events in a persistent SQLite Docker volume. It **does not import PIRO's shared database connection or change shared SQL/Solr data**. It uses a local case-derived roster when available, with a fictional 25-person fallback. All login events and work locations are simulated. No identity or location is collected from this computer.

The prototype is deliberately separate from production authentication and SQL Server deployment. Dashboard reads are unauthenticated and can include real staff names from the local roster; event writes require a random local token, and their published port is loopback-only. This remains a local demo, not a production staff-location service. The normal PIRO API container retains its existing configuration.

## Build the roster from recent PIRO cases

The separate exporter opens SQL Server with `readonly=True` and executes only the SELECT in `recent_case_profiles.sql`. It writes `roster.local.json`, which is ignored by Git and loaded by the presence API at startup. No tables, columns, indexes, views, shared data, or SQLite schema are changed.

From the repository root:

```sh
docker compose run --rm --no-deps -T -v ./prototypes/physician-location:/prototype api python /prototype/export_case_roster.py
docker compose --env-file prototypes/physician-location/.env.local -f docker-compose.yml -f docker-compose.override.yml -f prototypes/physician-location/compose.yml restart presence-api
docker compose --env-file prototypes/physician-location/.env.local -f docker-compose.yml -f docker-compose.override.yml -f prototypes/physician-location/compose.yml exec -T presence-api python send_synthetic_login.py --seed
```

Defaults select up to 25,000 of the newest active, completed cases accessioned in the last 90 calendar days, then keep the 25 eligible pathologists with the most linked cases. `--days`, `--max-cases`, and `--limit` adjust these bounds. `Case → CaseStaff → Staff` supplies names, and `SSIS_CaseStaff.RESPONSIBLE_ROLE_DESC = 'STAFF PATHOLOGIST'` supplies positive role evidence on at least one sampled case. The staging import covers only part of the sample, so the roster is a subset, not a complete staff directory. Generic staff links alone do not establish physician roles; fellows, cytotechnologists, and assistants without staff-pathologist evidence are excluded.

`Case → Specialty` supplies case specialties, and `Case → Hospital → Region` supplies case regions. Duplicate case/staff links are counted once. The local snapshot contains names and aggregate case counts, not patient details or case numbers. Stable staff-based demo IDs retain simulated event histories across refreshes; demo usernames are not real login accounts.

Subspecialty means the most frequent **mapped clinical case specialty**, not a verified staff appointment or certification. Clinical categories and explicit codes are mapped in `export_case_roster.py`; administrative values, named routing buckets, and unmapped labels are excluded. Ties display `Mixed case mix`, and no mapped evidence displays `Undetermined`. Expand a profile to see all mapped specialty counts and the total/recognized case counts. Case region is the most frequent case hospital region, not staff affiliation or physical presence. The UI labels locations and events as simulated, and the case sample does not change with the login observation date.

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

In this workspace, the prototype's services, UI mounts, and `presence_data` volume are also included in the Git-ignored `docker-compose.override.yml`. A normal Compose startup therefore retains the location route and starts the location service. The ingestion token is read directly from the existing `.env.local` file. To refresh only the prototype using the usual local configuration:

```sh
docker compose up -d --no-deps presence-api ui
```

Keep those prototype entries when editing the local override. On another checkout without them, use the three-file Compose command above; otherwise a normal UI recreate restores the standard nginx configuration and `/api/work-location/` returns 404. Both prototype services use `restart: unless-stopped`, and nginx refreshes the location-service address through Docker DNS after container replacement.

The prototype nginx configuration resolves the main API only when a normal PIRO API request is made, so this page can run while the main API is stopped.

## Send synthetic events from this Mac

```sh
set -a
. prototypes/physician-location/.env.local
set +a
python3 prototypes/physician-location/send_synthetic_login.py --seed
python3 prototypes/physician-location/send_synthetic_login.py --physician 1 --location remote
python3 prototypes/physician-location/send_synthetic_login.py --physician 1 --location office
python3 prototypes/physician-location/send_synthetic_login.py --physician 1 --location office --building 'Beachwood FHC'
python3 prototypes/physician-location/send_synthetic_login.py --physician 1 --location remote-session
```

Each invocation produces a distinct login. Seeding adds 19 logins: one office login at each of the 18 buildings and one remote login. Six physicians receive no seed event. Seeding is additive, not a reset. The prototype displays the latest event by occurrence time, even if older events arrive later. A remote-desktop session is classified Unknown; an off-site console event is Remote, never assumed to be a home address.

`buildings.json` is the shared location catalog for the API and both senders. It contains the 18 distinct nonblank values from `computer_list.xlsx`, `Onsite!E2:E151` (the Building column): LL, L, E, Weston, A, Union, Akron, Indian River, Fairview, CCAC, Q, Mercy, Hillcrest, Avon, Southpoint, Beachwood FHC, Marymount, and T. The WFH sheet has no populated Building values. Labels are preserved exactly, including letter codes; only building labels are copied, with fictional `DEMO-` device IDs. Default individual office logins cycle through this catalog by physician, or use `--building` / `-Building` to choose one. Organizational regions remain separate from observed buildings.

## PowerShell dummy sender

On a Windows computer running this local stack (or PowerShell on this Mac), provide the same local token in `PRESENCE_INGEST_TOKEN`, then run:

```powershell
./prototypes/physician-location/send-synthetic-login.ps1 -Physician 1 -Location Remote
./prototypes/physician-location/send-synthetic-login.ps1 -Physician 1 -Location Office
./prototypes/physician-location/send-synthetic-login.ps1 -Physician 1 -Location Office -Building 'Beachwood FHC'
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

- `GET /work-location/physicians?day=YYYY-MM-DD` — current prototype roster, source metadata, and selected-day simulated history; day defaults to America/New_York.
- `POST /work-location/events` — requires `X-Presence-Token` on the loopback port 8002.
- Required payload: `event_id` (UUID), `physician_id`, `username`, `device_id`, timezone-aware `occurred_at`, `synthetic: true`.
- Optional enums: `event_type: logon`, `session_type: console|remote`, `network_context: onsite|offsite|unknown`.
- Only demo identities from the loaded prototype roster are accepted. `synthetic: true` describes the login signals, while `roster.real_names` identifies the roster source. Device names must start with `DEMO-`. The server maps known devices to sites; unrecognized on-site devices yield Unknown.
- Event time and receipt time are both retained. More than five minutes of future clock skew is rejected.

## Tests

```sh
docker compose --env-file prototypes/physician-location/.env.local -f docker-compose.yml -f docker-compose.override.yml -f prototypes/physician-location/compose.yml run --rm --no-deps presence-api python -m unittest -v test_app
```

Tests cover credential rejection, prototype identity enforcement, duplicate/conflicting event IDs, multiple logins, delayed delivery, remote-session ambiguity, date boundaries, and timestamp validation. Add `test_case_roster` to the test command to check clinical specialty aggregation, unmapped labels, ties, and stable profile identities.

## Limits and next steps

This is a login-observation prototype, not a live attendance system. It does not infer physical presence, automatically expire today's observations, or resolve simultaneous sessions across multiple devices. It shows Unknown for ambiguous remote sessions. The UI says No Activity Today for an empty selected date, including historical dates. The optional real-name roster is a fixed local snapshot inferred from case links. No production Windows deployment, certificate authentication, event spool/retry agent, directory integration, or formal staff-specialty directory has been installed.

Before production, integrate role-protected reads, trustworthy session identity, managed device authentication, server-side IT location mappings, retention, and a SQL Server migration. The local token is only a prototype credential, not a recommended Windows rollout mechanism.

To return the UI to its usual nginx configuration, remove the prototype's UI override entries from the local `docker-compose.override.yml`, then recreate only the UI with the standard Compose files. Stop `presence-api` separately if desired; keep its volume to retain test history. No database reset is necessary.

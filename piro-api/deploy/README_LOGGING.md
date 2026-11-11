# API server logging

## Design

This configuration is for non-container Linux servers running systemd and
Gunicorn/Uvicorn. Local Uvicorn and Docker development retain console logging.

```text
Loguru + Python logging + Gunicorn/Uvicorn + raw stdout/stderr
    -> piro-api.service stdout/stderr
    -> journald (still available through journalctl)
    -> dedicated rsyslog imjournal collector
    -> backend/logs/runtime.log
```

One runtime file includes access records, errors, tracebacks, and startup output.
There is no application file sink and no direct systemd append-file sink.
`--capture-output` is unnecessary here: both process streams already go to
journald, and Gunicorn's capture redirection does not apply with `errorlog=-`.
The collector also selects systemd records whose `UNIT` is `piro-api.service`.
Other kernel/host diagnostics may still require the system journal.

The collector is a separate rsyslog instance, not a change to the host's default
rsyslog configuration. It has its own cursor, PID file, and 256 MB disk queue.
First start reads retained journal history; subsequent starts resume from the
cursor. Catch-up can take time on a large journal. Crash recovery may replay
records; this is not an exactly-once or guaranteed-lossless system. Do not
delete the collector state/queue directory during normal deployments.

Loguru defaults to `INFO`; use `PIRO_LOG_LEVEL=DEBUG` temporarily if necessary.
Its variable-value diagnostics are disabled. Internal request log entries omit
query strings, and caught errors retain tracebacks. External API errors retain
their existing privacy restrictions. Exception text, third-party output, server
access URLs, and existing validation messages can still contain sensitive data;
this change is not a comprehensive redaction layer. Restrict access to both
the journal and collected files. Do not enable SQL parameter logging.

## 1. Development server preflight

Perform these steps on the development server before production. Commands below
assume Debian/Ubuntu, service account `piro-user`, collector account `syslog`,
group `adm`, and these paths:

```text
API checkout: /opt/piro-api/piro-api
Python venv:  /opt/piro-api/piro-api_venv
API backend: /opt/piro-api/piro-api/backend
```

Adjust all templates and commands if the server differs. Do not replace existing
bind addresses, environment settings, service hardening, or executable paths
without checking the current deployment. The API unit template binds to
127.0.0.1:8000 for the documented NGINX reverse proxy; no NGINX changes are needed.
If the unit has a different name, change the collector's unit filters too.

Inspect the current unit and any drop-ins locally; their output may contain
secrets and should not be shared unredacted:

```bash
sudo systemctl cat piro-api.service
systemd --version
getent passwd syslog
getent group adm
getent group systemd-journal
sudo journalctl --disk-usage
```

Install `rsyslog` and `logrotate` with your server's package manager if absent
(on Debian/Ubuntu: `sudo apt-get install rsyslog logrotate`). Verify that the
installed rsyslog includes `imjournal`. The collector unit grants journal read
access through `SupplementaryGroups=systemd-journal`; no global group membership
change or default-rsyslog restart is required.

Back up the active API unit and its drop-ins outside the checkout. Deploy the
updated code and `deploy/` templates through your normal release process.
Keep old application and Gunicorn logs until verification is complete.

### Journal persistence and capacity

Check whether the journal is persistent across reboot. If not, coordinate with
the server administrator to set `Storage=persistent` in a journald configuration
drop-in. For example, an administrator-reviewed
`/etc/systemd/journald.conf.d/piro-api.conf` could contain:

```ini
[Journal]
Storage=persistent
SystemMaxUse=1G
SystemKeepFree=2G
MaxRetentionSec=14day
```

These are HOST-WIDE limits, not API-specific limits; choose values suitable for
the server, not blindly. Apply approved changes with
`sudo systemctl restart systemd-journald` and `sudo journalctl --flush`.
Journal retention must cover the longest expected collector outage. A full disk,
vacuumed journal, or overwhelmed queue can still cause loss. Monitor capacity.
The API unit disables per-service journal rate limiting to preserve error bursts;
the dedicated reader also disables its input limiter. This increases the need
to monitor log volume, disk space, and collector health.

## 2. Prepare permissions and install the collector

The following commands are run from the API checkout (the directory containing
`backend/` and `deploy/`), not the overall PIRO repository root:

```bash
cd /opt/piro-api/piro-api
sudo install -d -o syslog -g adm -m 0750 backend/logs
sudo touch backend/logs/runtime.log
sudo chown syslog:adm backend/logs/runtime.log
sudo chmod 0640 backend/logs/runtime.log
sudo install -d -o syslog -g adm -m 0700 /var/lib/piro-api-log-collector
namei -l /opt/piro-api/piro-api/backend/logs/runtime.log
```

Ensure `syslog` can traverse every parent directory. Grant only the required
traversal ACLs if necessary; do not make the checkout world-writable. Existing
systemd sandboxing, AppArmor, or SELinux policies may need administrator-approved
access to this destination. Do not disable those protections to make logging work.

Configure an AppArmor exception for piro-api.  Specifically, create the file
`/etc/apparmor.d/rsyslog.d/piro-api`:

```bash
sudo install -d -o root -g root -m 0755 /etc/apparmor.d/rsyslog.d
sudoedit /etc/apparmor.d/rsyslog.d/piro-api
```

And add exactly the following to that file:

```bash
/etc/rsyslog-piro-api.conf r,

/run/piro-api-log-collector/rsyslogd.pid rw,
/run/piro-api-log-collector/rsyslogd.pid.tmp rw,

/var/lib/piro-api-log-collector/ r,
/var/lib/piro-api-log-collector/** rw,

/opt/piro-api/piro-api/backend/logs/ r,
/opt/piro-api/piro-api/backend/logs/runtime.log rw,
```

Then reload the `rsyslog` configuration:

```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.rsyslogd
```

Then proceed...

```bash
sudo install -o root -g root -m 0644 deploy/rsyslog-piro-api.conf /etc/rsyslog-piro-api.conf
sudo install -o root -g root -m 0644 deploy/piro-api-log-collector.service /etc/systemd/system/piro-api-log-collector.service
sudo /usr/sbin/rsyslogd -N1 -f /etc/rsyslog-piro-api.conf
sudo systemd-analyze verify /etc/systemd/system/piro-api-log-collector.service
```

STOP and resolve any parser or permission error before enabling the collector.
Do not install this configuration into `/etc/rsyslog.d/`: it is a standalone
configuration with its own `imjournal` input, not a host-rsyslog drop-in.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now piro-api-log-collector.service
sudo systemctl status piro-api-log-collector.service
sudo journalctl -u piro-api-log-collector.service -n 50 --no-pager
```

## 3. Switch the API service to journal output

Merge `deploy/piro-api.service` into the existing API unit using
`sudo systemctl edit --full piro-api.service`. For a genuinely new installation,
install the reviewed template into `/etc/systemd/system/piro-api.service`.

Preserve the server's existing settings, but remove Gunicorn's old file
destinations and use `--access-logfile - --error-logfile -`. Ensure the effective
service has `StandardOutput=journal`, `StandardError=journal`,
`SyslogIdentifier=piro-api`, `PYTHONUNBUFFERED=1`, `PIRO_LOG_LEVEL=INFO`, and
`LogRateLimitIntervalSec=0`, as shown in the template. These environment values
must be in the service environment, not just an interactive shell. Existing
drop-ins can override the main unit; inspect the effective unit before restart.

```bash
sudo systemd-analyze verify /etc/systemd/system/piro-api.service
sudo systemctl daemon-reload
sudo systemctl restart piro-api.service
sudo systemctl status piro-api.service
sudo journalctl -u piro-api.service -n 50 --no-pager
sudo tail -n 50 backend/logs/runtime.log
```

Confirm Gunicorn startup messages and a normal request through NGINX appear in
both retrieval paths. No new `piro.log` should appear in the backend directory.
Do not treat existing historical files as evidence of new writes.

## 4. Exercise every logging source

On the DEVELOPMENT server only, add a temporary startup hook:

```bash
sudo install -d -m 0755 /etc/systemd/system/piro-api.service.d
sudoedit /etc/systemd/system/piro-api.service.d/90-logging-check.conf
```

Use the reviewed server paths in this drop-in:

```ini
[Service]
ExecStartPre=/opt/piro-api/piro-api_venv/bin/python /opt/piro-api/piro-api/deploy/check_logging.py
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart piro-api.service
sudo journalctl -u piro-api.service --since "5 minutes ago" --no-pager
sudo grep 'PIRO_LOGGING_CHECK_' backend/logs/runtime.log
```

Each probe run generates a fresh `PIRO_LOGGING_CHECK_<id>` with five marker
records: stdout, stderr, Loguru, standard logging, and traceback. Confirm all
five reach the journal and the file once for that fresh ID, plus the synthetic
RuntimeError's traceback lines. The synthetic exception is caught; the probe
exits successfully. Do not create real failures involving patient data.

If journal records exist but file records do not, check the collector service,
its permission to read the journal and traverse the destination path, and the
configured unit-name filter. If rsyslog is temporarily unavailable, continue
using `journalctl -u piro-api.service`; catch-up depends on journal retention.

## 5. Install and test rotation

Install the dedicated configuration OUTSIDE `/etc/logrotate.d/` to avoid having
the host's global scheduler rotate the same file with a different state file:

```bash
sudo install -o root -g root -m 0644 deploy/piro-api.logrotate /etc/piro-api-logrotate.conf
sudo install -o root -g root -m 0644 deploy/piro-api-logrotate.service /etc/systemd/system/piro-api-logrotate.service
sudo install -o root -g root -m 0644 deploy/piro-api-logrotate.timer /etc/systemd/system/piro-api-logrotate.timer
sudo systemd-analyze verify /etc/systemd/system/piro-api-logrotate.service /etc/systemd/system/piro-api-logrotate.timer
sudo logrotate --debug /etc/piro-api-logrotate.conf
sudo systemctl daemon-reload
sudo systemctl start piro-api-logrotate.service
sudo systemctl enable --now piro-api-logrotate.timer
sudo systemctl list-timers piro-api-logrotate.timer
```

On development, force a rotation, then restart the API with the temporary probe
still installed. The second probe ID must appear in the NEW runtime.log, not
only in runtime.log.1. Confirm normal requests still work:

```bash
sudo logrotate --force --state /var/lib/piro-api-logrotate/status /etc/piro-api-logrotate.conf
sudo systemctl restart piro-api.service
sudo grep 'PIRO_LOGGING_CHECK_' backend/logs/runtime.log
sudo journalctl -u piro-api-log-collector.service -n 50 --no-pager
sudo journalctl -u piro-api-logrotate.service -n 50 --no-pager
```

The policy checks hourly (with up to five minutes' scheduling jitter), rotates
daily or above 100 MB, keeps 14 archives, and compresses all but the newest
archive. These are archive counts, NOT 14 guaranteed days under high volume.
Rotation renames/creates files then sends HUP to the collector, not Gunicorn.
It does not truncate an open file or restart the API. Size is checked only when
the timer runs: this is not a hard storage cap. Tune thresholds/frequency and
monitor space for journal, queue, and archives, including compression headroom.

Verify collector downtime recovery on development: stop ONLY the collector,
restart the API once to emit a fresh probe ID, confirm it is in the journal,
then start the collector and confirm that ID is eventually in runtime.log.
The API should continue serving throughout the collector outage. Never remove
the cursor to force replay unless deliberately recovering from a known problem.

After testing, remove ONLY the temporary hook and reload systemd:

```bash
sudo rm /etc/systemd/system/piro-api.service.d/90-logging-check.conf
sudo systemctl daemon-reload
```

Do not remove the whole drop-in directory or other settings. Approve production
rollout only after syntax, five-source capture, access logging, rotation,
permissions, and outage recovery checks succeed on development.

## 6. Operations and rollback

Use `sudo tail -F backend/logs/runtime.log` (capital F follows rotation) and
`sudo journalctl -u piro-api.service -f`. Existing host syslog duplication is
unchanged; this dedicated collector neither reads nor stops host syslog rules.
Monitor collector/rotation unit failures and journal suppression warnings.

Leave old logs untouched until retention approval. Once old destinations stop
receiving writes, retire only API-specific obsolete rotation entries; a shared
`/etc/logrotate.d/gunicorn` may still be needed by other applications.

For collector problems, leave the API on journal output and use journalctl while
repairing the collector. For a full rollback, disable the dedicated rotation
timer, stop the collector, and restore the backed-up API unit and previous code
through the normal release process. Reload systemd and restart the API. Preserve
runtime archives, journal records, and collector state for investigation. Do not
disable or replace the host's default rsyslog service. A journald policy rollback
is a separate administrator-reviewed host-wide change.

## Local regression checks

From the overall PIRO repository root, using the project's Python environment:

```bash
python -m unittest discover -s piro-api/backend/tests -p test_logging.py -v
```

These isolated tests do not need a database or Solr. They verify console routing,
levels, duplicate prevention, tracebacks, the synthetic server probe, and basic
deployment contracts. They do not replace Linux parser checks or the actual
journal/collector/rotation acceptance tests above.

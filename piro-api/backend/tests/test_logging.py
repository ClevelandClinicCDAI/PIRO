import configparser
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BACKEND = Path(__file__).resolve().parents[1]
DEPLOY = BACKEND.parent / "deploy"


class LoggingTests(unittest.TestCase):
    def run_logging(self, source, level="INFO"):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(BACKEND)
        environment["PIRO_LOG_LEVEL"] = level
        with tempfile.TemporaryDirectory() as working_directory:
            result = subprocess.run(
                [sys.executable, "-c", source],
                cwd=working_directory,
                env=environment,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(list(Path(working_directory).iterdir()), [])
        return result

    def test_loguru_and_standard_logging_are_captured_once(self):
        result = self.run_logging(
            "import logging\n"
            "from logger import configure_logging, logger\n"
            "configure_logging()\n"
            "logger.info('application-marker')\n"
            "logging.getLogger('piro.external_api').info('library-marker')\n"
            "logger.debug('hidden-debug-marker')\n"
        )
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr.count("application-marker"), 1)
        self.assertEqual(result.stderr.count("library-marker"), 1)
        self.assertNotIn("hidden-debug-marker", result.stderr)
        self.assertIn("pid=", result.stderr)

    def test_log_level_is_configurable(self):
        result = self.run_logging(
            "import logging\n"
            "from logger import logger\n"
            "logger.debug('application-debug')\n"
            "logging.getLogger('piro.external_api').debug('library-debug')\n",
            level="DEBUG",
        )
        self.assertIn("application-debug", result.stderr)
        self.assertIn("library-debug", result.stderr)

    def test_tracebacks_do_not_dump_local_values(self):
        result = self.run_logging(
            "from logger import logger\n"
            "def fail():\n"
            "    values = {'credential': 'sensitive-local-marker'}\n"
            "    return values['missing']\n"
            "try:\n"
            "    fail()\n"
            "except KeyError:\n"
            "    logger.exception('operation failed')\n"
        )
        self.assertIn("Traceback", result.stderr)
        self.assertIn("KeyError: 'missing'", result.stderr)
        self.assertNotIn("sensitive-local-marker", result.stderr)

    def test_request_error_keeps_traceback_without_query_string(self):
        result = self.run_logging(
            "import asyncio\n"
            "from fastapi import Request\n"
            "from exception_handlers import log_error\n"
            "request = Request({'type': 'http', 'method': 'GET', "
            "'path': '/logging-check', 'headers': [], "
            "'query_string': b'token=sensitive-query-marker', "
            "'client': ('127.0.0.1', 1234)})\n"
            "try:\n"
            "    raise RuntimeError('request-failure-marker')\n"
            "except RuntimeError as exc:\n"
            "    failure = exc\n"
            "asyncio.run(log_error(request, failure))\n"
        )
        self.assertIn("GET /logging-check", result.stderr)
        self.assertIn("Traceback", result.stderr)
        self.assertIn("RuntimeError: request-failure-marker", result.stderr)
        self.assertNotIn("sensitive-query-marker", result.stderr)

    def test_server_probe_exercises_all_logging_sources(self):
        result = self.run_logging(
            "import runpy\n"
            f"runpy.run_path({str(DEPLOY / 'check_logging.py')!r}, "
            "run_name='__main__')\n"
        )
        self.assertIn("PIRO_LOGGING_CHECK_", result.stdout)
        self.assertIn("stdout", result.stdout)
        self.assertIn("stderr", result.stderr)
        self.assertIn("loguru", result.stderr)
        self.assertIn("standard_logging", result.stderr)
        self.assertIn("RuntimeError: Synthetic logging", result.stderr)


class DeploymentLoggingTests(unittest.TestCase):
    def test_api_leaves_both_streams_in_the_journal(self):
        config = configparser.ConfigParser(interpolation=None, strict=False)
        config.read(DEPLOY / "piro-api.service")
        service = config["Service"]
        self.assertEqual(service["StandardOutput"], "journal")
        self.assertEqual(service["StandardError"], "journal")
        self.assertIn("--access-logfile -", service["ExecStart"])
        self.assertIn("--error-logfile -", service["ExecStart"])
        self.assertNotIn("/var/log/gunicorn", service["ExecStart"])

    def test_collector_is_isolated_and_rotation_reopens_its_file(self):
        collector = (DEPLOY / "rsyslog-piro-api.conf").read_text()
        rotation = (DEPLOY / "piro-api.logrotate").read_text()
        self.assertIn('StateFile="journal.state"', collector)
        self.assertIn('$!_SYSTEMD_UNIT == "piro-api.service"', collector)
        self.assertIn('queue.saveOnShutdown="on"', collector)
        self.assertIn("--signal=HUP piro-api-log-collector.service", rotation)
        self.assertNotIn("copytruncate", rotation)
        self.assertIn("rotate 14", rotation)

    def test_rotation_has_an_independent_hourly_schedule(self):
        config = configparser.ConfigParser(interpolation=None)
        config.read(DEPLOY / "piro-api-logrotate.timer")
        self.assertEqual(config["Timer"]["OnCalendar"], "hourly")
        self.assertEqual(config["Timer"]["Unit"], "piro-api-logrotate.service")
        config.read(DEPLOY / "piro-api-logrotate.service")
        command = config["Service"]["ExecStart"]
        self.assertIn("/var/lib/piro-api-logrotate/status", command)
        self.assertNotIn("/etc/logrotate.d/", command)


if __name__ == "__main__":
    unittest.main()

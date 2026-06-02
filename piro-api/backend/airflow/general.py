import requests

from pathlib import Path

from core.config import Settings
from logger import logger


def get_application_root_directory() -> Path | None:
    """Return the path to the application's root directory

    We define the 'root' as the directory containing
    the magic_dags.py file.  We start with the directory of
    the executing file and check each parent, in turn, until
    we find the root directory."""
    current_file_path = Path(__file__).resolve()
    for directory in current_file_path.parents:
        airflow_dag_path = directory / "main.py"
        if airflow_dag_path.exists():
            return directory
    return None


def get_certificates_directory() -> Path | None:
    application_root_directory: Path | None = get_application_root_directory()
    if application_root_directory:
        return application_root_directory / "certificates"


def get_certificate_path_airflow() -> Path:
    certificates_directory: Path | None = get_certificates_directory()
    certname = Settings.AIRFLOW_CERTIFICATE
    if certificates_directory is None or not certname:
        raise FileNotFoundError("Certificates directory not found")
    return certificates_directory / certname


def get_airflow_api_token(base_url: str, cert_path: str) -> str | None:
    """Obtain a JWT Bearer token from the Airflow 3 auth endpoint.

    Typically for use with the Airflow API."""

    token_url: str = f"{base_url}/auth/token"
    payload: dict = {
        "username": Settings.AIRFLOW_USERNAME,
        "password": Settings.AIRFLOW_PASSWORD,
    }
    response: requests.Response = requests.post(
        token_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        verify=cert_path,
    )
    if response.status_code not in (200, 201):  # May return 201 on success
        logger.error(
            f"Failed to obtain Airflow token: {response.status_code}, {response.reason}"  # noqa:E501
        )
        return None
    return response.json().get("access_token")

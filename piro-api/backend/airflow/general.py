from pathlib import Path

from core.config import Settings


def get_application_root_directory() -> Path:
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


def get_certificates_directory() -> Path:
    application_root_directory: Path = get_application_root_directory()
    return application_root_directory / "certificates"


def get_certificate_path_airflow() -> Path:
    certname = Settings.AIRFLOW_CERTIFICATE
    certificates_path: str = f"{get_certificates_directory()}/{certname}"
    return certificates_path

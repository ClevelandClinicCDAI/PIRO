from pathlib import Path
from dotenv import load_dotenv
from airflow.sdk import Variable


def get_application_root_directory() -> Path:
    """Return the path to the application's root directory
    We define the 'root' as the directory containing
    the magic_dags.py file.  We start with the directory of
    the executing file and check each parent, in turn, until
    we find the root directory."""
    current_file_path = Path(__file__).resolve()
    for directory in current_file_path.parents:
        airflow_dag_path = directory / "piro_dags.py"
        if airflow_dag_path.exists():
            return directory
    raise FileNotFoundError(
        "Could not find the application's root directory. "
        "Expected to find 'piro_dags.py' in one of the parent directories."
    )


def get_certificates_directory() -> Path:
    application_root_directory: Path = get_application_root_directory()
    return application_root_directory / "certificates"


def get_certificate_path_solr() -> str:
    load_dotenv()
    certName = Variable.get("SOLR_CERTIFICAT_NAME")
    certificates_path: str = f"{get_certificates_directory()}/{certName}"
    return certificates_path


def get_certificate_path_concentriq() -> str:
    load_dotenv()
    certName = Variable.get("CONCENTRIQ_CERTIFICAT_NAME")
    certificates_path: str = f"{get_certificates_directory()}/{certName}"
    return certificates_path

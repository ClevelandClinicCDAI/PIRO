from dotenv import load_dotenv
from airflow.models import Variable
from tasks.utils.logging_setup import get_logger

logger = get_logger()


def get_var(varname: str) -> str:
    load_dotenv()
    varVal = Variable.get(varname)
    if "PASSWORD" not in varname.upper():
        logger.info(f"{varname} configuration - {varVal}")
    if varVal is None:
        raise Exception(f"Configuraton not found: {varname}")
    return varVal


def set_var(varname: str, varval: str):
    load_dotenv()
    varVal = Variable.get(varname)
    if varVal is None:
        raise Exception(f"Configuraton not found: {varname}")
    Variable.set(key=varname, value=varval)


from dotenv import load_dotenv
from airflow.sdk import Variable

load_dotenv()


def get_var(varname: str) -> str:
    variable_value = Variable.get(varname)
    if variable_value is None:
        raise Exception(f"Airflow variable not found: {varname}")
    return variable_value


def set_var(varname: str, varval: str):
    variable_value = Variable.get(varname)
    if variable_value is None:
        raise Exception(f"Variable not found: {varname}")
    Variable.set(key=varname, value=varval)

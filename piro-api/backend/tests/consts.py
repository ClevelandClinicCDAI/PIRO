from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

sqlite_dir = BASE_DIR / "backend" / "tests"

SQLA_DB_URL = f"sqlite:///{sqlite_dir.resolve() / 'fuzzy.db'}"

file_name_model_dict = {
    "role": "Role",
    "search": "Search",
    "searchrequest": "SearchRequest",
    "searchrequeststatus": "SearchRequestStatus",
    "tag": "Tag",
    "tagcase": "TagCase",
    "user": "User",
    "userrole": "UserRole",
}

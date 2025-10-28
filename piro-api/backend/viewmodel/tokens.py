from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLoginVM(BaseModel):
    username: str
    password: str
    islog: bool

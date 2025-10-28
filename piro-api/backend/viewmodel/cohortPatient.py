from pydantic import BaseModel
from typing import Optional


# properties required during user creation
class CohortPatientVMCreate(BaseModel):
    cohortId: int
    mrn: str


class CohortPatientVM:
    cohortId: int
    mrn: str
    epi: str
    isfound: Optional[bool]

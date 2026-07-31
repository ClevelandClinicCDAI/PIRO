from enum import Enum


class Constants:
    class SearchRequestStatus(Enum):
        SUBMIT = 1
        APPROVE = 2
        DENY = 3
        CLOSE = 4

    class SearchRequestAction(Enum):
        SUBMIT = 1
        APPROVE = 2
        DENY = 3
        DELETE = 4
        DOWNLOAD = 5
        EXPORT = (6,)
        UPDATE = 7

    class SlideRequestStatus(Enum):
        PENDING = "PENDING"
        HOLDING = "HOLDING"
        IN_PROCESS = "IN_PROCESS"
        COMPLETED = "COMPLETED"
        NIF = "NIF"
        CANCELED = "CANCELED"

    class SlideRequestUrgency(str, Enum):
        PRIORITY = "Priority"
        ROUTINE = "Routine"

    class SlideRequestReason(str, Enum):
        SIGN_OUT = "Sign Out"
        ADDITIONAL_TESTING = "Additional Testing"
        CAP_INSPECTION = "Cap Inspection"
        CONFERENCE = "Conference"
        QA = "QA"
        SEND_OUTS = "Send Outs"
        TUMOR_BOARD = "Tumor Board"
        VALIDATION = "Validation"

    class SlideRequestCaseType(str, Enum):
        SURGICAL = "Surgical"
        CYTOLOGY = "Cytology"

    class StatusCode(Enum):
        S = 1
        W = 2
        E = 3

    class LoginTypeCode(Enum):
        CREDENTIAL = 1
        AD = 2
        ADGROUP = 3
        ACCOUNT = 4
        ROLE = 5
        ATTEST = 6
        TOKEN = 7
        OAUTH = 8

    CommentTypeFinalDiagnosis: str = "FINAL DIAGNOSIS"
    CommentTypeFlowCytometry: str = "FLOW CYTOMETRY RESULTS"
    CommentTypeFinalCoPath: str = "$final"
    CommentTypeFinal: str = "Final"

    RoleAdmin: str = "ADMIN"
    RoleSecurityAdmin: str = "SECURITYADMIN"
    RoleUser: str = "USER"
    RoleAnalyst: str = "ANALYST"
    RoleDemoAdmin: str = "DEMOADMIN"
    RoleSlideRoom: str = "SLIDEROOM"

    # AttestationText: str = "<p>Attestation Text</p><br/>I <b>attest</b> the application....."
    # AttestationRequiredDate: str = "2024-06-12"

    AppConfigurationAttestationCertificatoinText: str = (
        "Attestation.CertificatoinText"
    )
    AppConfigurationAttestationRequiredDate: str = "Attestation.RequiredDate"
    AppConfigurationAttestationEnable: str = "Attestation.Enable"

    CohortTypeCase: str = "C"
    CohortTypeMrn: str = "P"
    CohortTypeEpi: str = "E"

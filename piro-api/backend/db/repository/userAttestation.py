from db.models.UserAttestation import UserAttestation
from db.models.ApplicationConfiguration import ApplicationConfiguration
from sqlalchemy.orm import Session
from core.constants import Constants
from db.dict2Class import dict2Class
from datetime import datetime


def create_new_attestation(userId: int, user: str, db: Session):
    attest = UserAttestation(
        UserId=userId,
        IsActive=True,
        CreateBy=user,
    )
    db.add(attest)
    db.commit()
    return attest


def get_attestation(userId: int, db: Session):
    attest = (
        db.query(UserAttestation)
        .filter(UserAttestation.UserId == userId)
        .first()
    )
    attestationEnable = (
        db.query(ApplicationConfiguration)
        .filter(
            ApplicationConfiguration.ConfigName
            == Constants.AppConfigurationAttestationEnable
        )
        .first()
    )
    attestationRequiredDateStr = (
        db.query(ApplicationConfiguration)
        .filter(
            ApplicationConfiguration.ConfigName
            == Constants.AppConfigurationAttestationRequiredDate
        )
        .first()
    )

    enableAttest: bool = False
    if attestationEnable is not None:
        enableAttest = (
            True if attestationEnable.ConfigValue == "Yes" else False
        )

    requireAttest: bool = False
    if attestationRequiredDateStr is not None:
        attestationRequiredDate = datetime.strptime(
            attestationRequiredDateStr.ConfigValue, "%Y-%m-%d"
        )
        requireAttest: bool = attestationRequiredDate < datetime.now()

    if attest is None:
        attestationTextStr = (
            db.query(ApplicationConfiguration)
            .filter(
                ApplicationConfiguration.ConfigName
                == Constants.AppConfigurationAttestationCertificatoinText
            )
            .first()
        )
        return dict2Class(
            {
                "IsAttest": False,
                "TextAttest": (
                    ""
                    if attestationTextStr is None
                    else attestationTextStr.ConfigValue
                ),
                "CreateDate": datetime.now(),
                "RequireAttest": requireAttest,
                "AttestationEnable": enableAttest,
            }
        )
    else:
        return dict2Class(
            {
                "IsAttest": True,
                "TextAttest": "",
                "CreateDate": attest.CreateDate,
                "RequireAttest": requireAttest,
                "AttestationEnable": enableAttest,
            }
        )


def get_is_attested(userId: int, db: Session):
    attest = (
        db.query(UserAttestation)
        .filter(UserAttestation.UserId == userId)
        .first()
    )
    return False if attest is None else True

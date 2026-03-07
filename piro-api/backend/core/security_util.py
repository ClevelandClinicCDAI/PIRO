from typing import Any
from core.constants import Constants
from db.views.VCase import VCase
from solr.models.document import document
import re


class SecurityUtil:
    "A collection of utilities for preventing unauthorized users from accessing protected attributes."

    search_ADMIN: str = ""
    search_ANALYST: str = (
        "collectiondate,signoutdate,receivedate,accessiondate,isdeceased,dob,patientname,patientdeathdate,overduedate"  # noqa
    )
    search_USER: str = (
        "collectiondate,signoutdate,receivedate,accessiondate,isdeceased,dob,patientname,patientdeathdate,overduedate"  # noqa
    )
    search_SECURITYADMIN: str = (
        "collectiondate,signoutdate,receivedate,accessiondate,isdeceased,dob,patientname,patientdeathdate,overduedate"  # noqa
    )
    search_DEMOADMIN: str = (
        "collectiondate,signoutdate,receivedate,accessiondate,isdeceased,dob,patientname,patientdeathdate,overduedate,casenumber,specimennumber"  # noqa
    )

    case_ADMIN: str = ""
    case_ANALYST: str = (
        "AccessionDate,ReceiveDate,OverdueDate,CollectionDate,SignoutDate,PatientName,PatientDOB,PatientEpi,PatientMrn,PatientLanguage,PatientEthnicity,PatientDeathDate,PatientIsDeceased,PatientRace,PatientCity,PatientState,PatientCountry"  # noqa
    )
    case_USER: str = (
        "AccessionDate,ReceiveDate,OverdueDate,CollectionDate,SignoutDate,PatientName,PatientDOB,PatientEpi,PatientMrn,PatientLanguage,PatientEthnicity,PatientDeathDate,PatientIsDeceased,PatientRace,PatientCity,PatientState,PatientCountry"  # noqa
    )
    case_SECURITYADMIN: str = (
        "AccessionDate,ReceiveDate,OverdueDate,CollectionDate,SignoutDate,PatientName,PatientDOB,PatientEpi,PatientMrn,PatientLanguage,PatientEthnicity,PatientDeathDate,PatientIsDeceased,PatientRace,PatientCity,PatientState,PatientCountry"  # noqa
    )
    case_DEMOADMIN: str = (
        "AccessionDate,ReceiveDate,OverdueDate,CollectionDate,SignoutDate,PatientName,PatientDOB,PatientEpi,PatientMrn,PatientLanguage,PatientEthnicity,PatientDeathDate,PatientIsDeceased,PatientRace,PatientCity,PatientState,PatientCountry,CaseNumber,RefRequisitionKey"  # noqa
    )

    @staticmethod
    def print_attr(obj: Any):
        """Print out all of an object's attributes."""
        for att in dir(obj):
            print(att, getattr(obj, att))

    @staticmethod
    def search(doc: document, role: str, isAttest: bool):
        """Remove protected attributes from a search result document."""

        excludes: str = ""
        if role == Constants.RoleDemoAdmin:
            excludes = SecurityUtil.search_DEMOADMIN
        elif isAttest is True:
            excludes = SecurityUtil.search_ADMIN
        elif role == Constants.RoleAdmin:
            excludes = SecurityUtil.search_ADMIN
        elif role == Constants.RoleAnalyst:
            excludes = SecurityUtil.search_ANALYST
        elif role == Constants.RoleUser:
            excludes = SecurityUtil.search_USER
        elif role == Constants.RoleSecurityAdmin:
            excludes = SecurityUtil.search_SECURITYADMIN

        excludes_arr = excludes.split(",")
        for exclude in excludes_arr:
            SecurityUtil.delete_attr(doc, exclude)

        if role == Constants.RoleDemoAdmin:
            doc.comment = SecurityUtil.mask_date(doc.comment)
            doc.comment = SecurityUtil.mask_case(doc.comment)

            doc.addend = SecurityUtil.mask_date(doc.addend)
            doc.addend = SecurityUtil.mask_case(doc.addend)

            doc.intraop = SecurityUtil.mask_date(doc.intraop)
            doc.intraop = SecurityUtil.mask_case(doc.intraop)

            doc.resident = SecurityUtil.mask_date(doc.resident)
            doc.resident = SecurityUtil.mask_case(doc.resident)

            # doc.synoptic = SecurityUtil.mask_date(doc.synoptic)
            # doc.synoptic = SecurityUtil.mask_case(doc.synoptic)

            # doc.gross = SecurityUtil.mask_date(doc.gross)
            # doc.gross = SecurityUtil.mask_case(doc.gross)

            doc.final = SecurityUtil.mask_date(doc.final)
            doc.final = SecurityUtil.mask_case(doc.final)

            doc.microscopic = SecurityUtil.mask_date(doc.microscopic)
            doc.microscopic = SecurityUtil.mask_case(doc.microscopic)

    @staticmethod
    def case(vcase: VCase, role, isAttest):
        """Remove protected attributes from a VCase object."""

        excludes: str = ""
        if role == Constants.RoleDemoAdmin:
            excludes = SecurityUtil.case_DEMOADMIN
        elif isAttest is True:
            excludes = SecurityUtil.case_ADMIN
        elif role == Constants.RoleAdmin:
            excludes = SecurityUtil.case_ADMIN
        elif role == Constants.RoleAnalyst:
            excludes = SecurityUtil.case_ANALYST
        elif role == Constants.RoleUser:
            excludes = SecurityUtil.case_USER
        elif role == Constants.RoleSecurityAdmin:
            excludes = SecurityUtil.case_SECURITYADMIN
        # elif role == Constants.RoleDemoAdmin:
        #     excludes = SecurityUtil.case_DEMOADMIN
        excludes_arr = excludes.split(",")
        for exclude in excludes_arr:
            SecurityUtil.delete_attr(vcase, exclude)

        return excludes_arr

    @staticmethod
    def comment_text(comments: Any, role):
        if comments is not None and role == Constants.RoleDemoAdmin:
            for row in comments:
                row.CommentText = SecurityUtil.mask_date(row.CommentText)
                row.CommentText = SecurityUtil.mask_case(row.CommentText)

    @staticmethod
    def mask_date(text: str):
        text = SecurityUtil.match_mask_text(
            text, "[0-9]{1,4}[-|\\/][0-9]{1,4}[-|\\/][0-9]{1,4}", "MM/dd/yyyy"
        )
        text = SecurityUtil.match_mask_text(
            text,
            "(January|February|March|April|May|June|July|August|September|October|November|December|jan|feb|mar|apr|May|jun|Jul|aug|sep|sept|oct|nov|dec)([-| |\\/|,|\\.|;]{0,2})([0-9]{1,4})([-| |\\/|,|\\.|;]{0,2})([0-9]{0,4})",
            "Month dd, yyyy",
        )  # noqa
        text = SecurityUtil.match_mask_text(
            text,
            "([0-9]{1,4})([-| |\\/|,|\\.|;]{0,2})(January|February|March|April|May|June|July|August|September|October|November|December|jan|feb|mar|apr|May|jun|Jul|aug|sep|sept|oct|nov|dec)([-| |\\/|,|\\.|;]{0,2})([0-9]{0,4})",
            "yyyy, Month dd",
        )  # noqa
        return text

    @staticmethod
    def mask_case(text: str):
        text = SecurityUtil.match_mask_text(
            text, "\\w{1,5}[\\d]{1,2}-[\\d]{1,8}", "X01-XXXXXX"
        )
        return text

    @staticmethod
    def match_mask_text(text: str, reg_exp: str, replace_text: str):
        group_matches = re.findall(reg_exp, text, re.IGNORECASE)
        # matchWord: str = ""
        if group_matches is not None:
            for group_match in group_matches:
                matchWord: str = ""
                for match in group_match:
                    matchWord = f"{matchWord}{match}"

                if matchWord != "":
                    # text = text.replace(matchWord, f"<b>{matchWord}</b>: {replace_text}")
                    # text = text.replace(matchWord, f"<b>{replace_text}</b>")
                    text = text.replace(matchWord, f"{replace_text}")
        return text

    @staticmethod
    def delete_attr(obj, name):
        """Remove an attribute from an object."""
        if hasattr(obj, name):
            delattr(obj, name)

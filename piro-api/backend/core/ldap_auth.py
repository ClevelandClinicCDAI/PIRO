import re
import ldap
import ldap.filter
from logger import logger
from core.config import Settings
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from core.constants import Constants
from db.repository.user import create_user_log

load_dotenv()

SUCCESS: str = Constants.StatusCode.S.name
ERROR: str = Constants.StatusCode.E.name

CREDENTIAL: str = Constants.LoginTypeCode.CREDENTIAL.name
AD: str = Constants.LoginTypeCode.AD.name
ADGROUP: str = Constants.LoginTypeCode.ADGROUP.name


def get_ldap_client() -> ldap.ldapobject.LDAPObject:
    """Configure necessary options and initialize an LDAP object (a 'client')."""

    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
    return ldap.initialize(Settings.AD_LDAP_PATH)


def user_login(userName: str, password: str, islog: bool, db: Session) -> bool:
    """Confirm the validity of a userName and password by attempting to bind to our LDAP server."""

    username_regex_match: re.Match | None = re.search(
        "^[a-zA-Z0-9_]*$", userName
    )
    if username_regex_match is None:
        message: str = (
            f"Invalid username during user login; Format validation: {userName}."
        )
        logger.error(message)
        create_user_log(
            userName, -1, -1, ERROR, CREDENTIAL, message, islog, db=db
        )
        return False

    ldap_client = get_ldap_client()
    try:
        user_has_valid_credentials: bool = try_ldap_bind(
            ldap_client, userName, password
        )
        if user_has_valid_credentials:
            message = f"User '{userName}' successfully bound to LDAP server."
            logger.info(message)
            create_user_log(
                userName, -1, -1, SUCCESS, CREDENTIAL, message, islog, db=db
            )
        else:
            message = f"User '{userName}' failed to bind to the LDAP server. Credentials failed"
            logger.error(message)
            create_user_log(
                userName, -1, -1, ERROR, CREDENTIAL, message, islog, db=db
            )

    except ldap.LDAPError as e:
        message = f"Error to binding to LDAP server. userName: '{userName}'. Error: {e}."
        logger.error(message)
        create_user_log(userName, -1, -1, ERROR, AD, message, islog, db=db)
        ldap_client.unbind()
        return False

    ldap_client.unbind()
    return user_has_valid_credentials


def try_ldap_bind(
    ldap_client: ldap.ldapobject.LDAPObject, userName: str, password: str
) -> bool:
    """Attempt an LDAP bind using the provided username and password.

    This serves to both establish the connection to the server ('bind') and
    validate the provided username and password."""

    try:
        escaped_username: str = ldap.filter.escape_filter_chars(userName)
        ldap_client.simple_bind_s(
            f"{escaped_username}@{Settings.AD_DOMAIN}", password
        )
        return True
    except ldap.INVALID_CREDENTIALS:
        return False


def user_group(userName: str, password: str, islog: bool, db: Session) -> bool:
    """Determine whether or not a user is a member of an AD group via LDAP query."""

    ldap_client = get_ldap_client()

    try:
        user_is_a_group_member: bool = check_if_user_is_in_group(
            ldap_client,
            username=userName,
            password=password,
            auth_group_name=Settings.AD_SECURITY_GROUP,
        )
        if user_is_a_group_member:
            message = f"User '{userName}' is authorized via group '{Settings.AD_SECURITY_GROUP}'"
            logger.info(message)
            create_user_log(
                userName, -1, -1, SUCCESS, ADGROUP, message, islog, db=db
            )
        else:
            message = f"User '{userName}' is NOT authorized via group '{Settings.AD_SECURITY_GROUP}'."
            logger.error(message)
            create_user_log(
                userName, -1, -1, ERROR, ADGROUP, message, islog, db=db
            )

    except ldap.LDAPError as e:
        message = f"LDAP error while checking if a user is in a group. userName: '{userName}'. Error: {e}."
        logger.error(message)
        create_user_log(userName, -1, -1, ERROR, AD, message, islog, db=db)
        ldap_client.unbind()
        return False

    ldap_client.unbind()
    return user_is_a_group_member


def check_if_user_is_in_group(
    ldap_client: ldap.ldapobject.LDAPObject,
    username: str,
    password: str,
    auth_group_name: str,
) -> bool:
    """Perform an LDAP query to confirm that a user is in a group."""

    escaped_username: str = ldap.filter.escape_filter_chars(username)
    ldap_client.simple_bind_s(
        f"{escaped_username}@{Settings.AD_DOMAIN}", password
    )
    search_results = ldap_client.search_s(
        base="dc=cc,dc=ad,dc=cchs,dc=net",
        scope=ldap.SCOPE_SUBTREE,
        filterstr=f"(sAMAccountName={escaped_username})",
        attrlist=["memberOf"],
    )

    if search_results:
        try:
            groups = search_results[0][1]["memberOf"]
        except (IndexError, AttributeError):
            return False

        for group_name in groups:
            if group_name.decode("utf-8").lower() == auth_group_name.lower():
                return True
        return False

    else:
        return False


def user_display_name(
    userName: str, password: str, islog: bool, db: Session
) -> dict | None:
    """Retrieve the user's display name (first and last) via LDAP."""

    ldap_client = get_ldap_client()

    try:
        user_details = get_user_displayname_ldap(
            ldap_client, username=userName, password=password, db=db
        )
        message = f"User's display name successfully retrieved via LDAP. userName: '{userName}'."
        logger.info(message)
        create_user_log(userName, -1, -1, SUCCESS, AD, message, islog, db=db)
    except ldap.LDAPError as e:
        message = f"LDAP error while looking up a user's display name. username: '{userName}'. Error: {e}."
        logger.error(message)
        create_user_log(userName, -1, -1, ERROR, AD, message, islog, db=db)
        ldap_client.unbind()
        return None

    ldap_client.unbind()
    return user_details


def get_user_displayname_ldap(
    ldap_client: ldap.ldapobject.LDAPObject,
    username: str,
    password: str,
    db: Session,
):
    """Perform an LDAP query to get the user's first and last name."""

    escaped_username: str = ldap.filter.escape_filter_chars(username)
    ldap_client.simple_bind_s(
        f"{escaped_username}@{Settings.AD_DOMAIN}", password
    )
    search_results = ldap_client.search_s(
        base="dc=cc,dc=ad,dc=cchs,dc=net",
        scope=ldap.SCOPE_SUBTREE,
        filterstr=f"(sAMAccountName={escaped_username})",
        attrlist=["sn", "givenName"],
    )

    if search_results:
        try:
            sns = search_results[0][1]["sn"]
            givenNames = search_results[0][1]["givenName"]
            firstName: str = ""
            lastName: str = ""

            if sns is not None:
                lastName = sns[0]

            if givenNames is not None:
                firstName = givenNames[0]

            return {"lastName": lastName, "firstName": firstName}

        except (IndexError, AttributeError):
            return {"lastName": "", "firstName": ""}
    else:
        return {"lastName": "", "firstName": ""}

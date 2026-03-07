from core.security_util import SecurityUtil
from core.constants import Constants
from solr.models.document import document


def test_print_attr(vcase_one):
    """Test the 'print_attr' method.

    Nothing to assert, but should run without error."""

    SecurityUtil.print_attr(obj=vcase_one)


def test_search_admin_not_attested():
    """Test the 'search' method with 'admin' role for a user who hasn't done the attestation.

    No attributes should be removed."""

    doc = document()
    original_attrs_list = doc.__dict__

    SecurityUtil.search(doc, role=Constants.RoleAdmin, isAttest=False)

    assert doc.__dict__ == original_attrs_list


def test_search_admin_attested():
    """Test the 'search' method with 'admin' role for a user who HAS done the attestation.

    No attributes should be removed."""

    doc = document()
    original_attrs_list = doc.__dict__

    SecurityUtil.search(doc, role=Constants.RoleAdmin, isAttest=True)

    assert doc.__dict__ == original_attrs_list


def test_search_user_not_attested():
    """Test the 'search' method with 'user' role for a user who hasn't done the attestation.

    Some attributes should be removed."""

    doc = document()

    SecurityUtil.search(doc, role=Constants.RoleUser, isAttest=False)

    assert not hasattr(doc, "patientname")


def test_search_user_attested():
    """Test the 'search' method with 'user' role for a user who HAS done the attestation.

    No attributes should be removed."""

    doc = document()
    original_attrs_list = doc.__dict__

    SecurityUtil.search(doc, role=Constants.RoleUser, isAttest=True)

    assert doc.__dict__ == original_attrs_list


def test_search_demoadmin_masks_microscopic():
    """Test DemoAdmin masking also redacts microscopic text content."""

    doc = document()
    for field in ["comment", "addend", "intraop", "resident", "final", "microscopic"]:
        setattr(doc, field, "MICROSCOPIC Patient 12/12/2020 case AB12-12345")

    SecurityUtil.search(doc, role=Constants.RoleDemoAdmin, isAttest=False)

    assert doc.microscopic == "MICROSCOPIC Patient MM/dd/yyyy case X01-XXXXXX"


def test_case_user_not_attested(vcase_one):
    """Test the 'case' method with 'user' role for a user who hasn't done the attestation.

    Some attributes should be removed.

    Note that the INSTANCE attribute will be removed, but class attribute continues to exist
    as part of the model; so we test to ensure the original value has been removed."""

    SecurityUtil.case(vcase_one, role=Constants.RoleUser, isAttest=False)

    assert vcase_one.PatientName is None


def test_case_user_attested(vcase_one):
    """Test the 'case' method with 'user' role for a user who HAS done the attestation.

    No attributes should be removed."""

    original_attrs_list = vcase_one.__dict__

    SecurityUtil.case(vcase_one, role=Constants.RoleUser, isAttest=True)

    assert vcase_one.__dict__ == original_attrs_list

import pytest

from app.api.dependencies import (
    check_study_access,
    check_study_write_access,
    check_study_manage_access,
)
from app.models.user_study import UserStudy


def _link(db_session, user, study, role):
    link = UserStudy(user_id=user.id, study_id=study.id, study_role=role)
    db_session.add(link)
    db_session.commit()
    return link


def test_admin_has_access_to_any_study(db_session, admin_user, study):
    assert check_study_access(study.id, admin_user, db_session) is True
    assert check_study_write_access(study.id, admin_user, db_session) is True
    assert check_study_manage_access(study.id, admin_user, db_session) is True


def test_researcher_without_membership_has_no_access(db_session, researcher_user, study):
    assert check_study_access(study.id, researcher_user, db_session) is False
    assert check_study_write_access(study.id, researcher_user, db_session) is False
    assert check_study_manage_access(study.id, researcher_user, db_session) is False


def test_researcher_with_viewer_role_reads_but_cannot_write(db_session, researcher_user, study):
    _link(db_session, researcher_user, study, "viewer")
    assert check_study_access(study.id, researcher_user, db_session) is True
    assert check_study_write_access(study.id, researcher_user, db_session) is False
    assert check_study_manage_access(study.id, researcher_user, db_session) is False


def test_researcher_with_researcher_role_can_write_but_not_manage(db_session, researcher_user, study):
    _link(db_session, researcher_user, study, "researcher")
    assert check_study_access(study.id, researcher_user, db_session) is True
    assert check_study_write_access(study.id, researcher_user, db_session) is True
    assert check_study_manage_access(study.id, researcher_user, db_session) is False


def test_researcher_with_admin_study_role_can_manage(db_session, researcher_user, study):
    _link(db_session, researcher_user, study, "admin")
    assert check_study_access(study.id, researcher_user, db_session) is True
    assert check_study_write_access(study.id, researcher_user, db_session) is True
    assert check_study_manage_access(study.id, researcher_user, db_session) is True


def test_global_viewer_role_never_gets_write_access_even_with_study_role(db_session, viewer_user, study):
    # global role gates first: viewer users can't write regardless of a stray study-role row.
    _link(db_session, viewer_user, study, "admin")
    assert check_study_access(study.id, viewer_user, db_session) is True
    assert check_study_write_access(study.id, viewer_user, db_session) is False
    assert check_study_manage_access(study.id, viewer_user, db_session) is False


def test_study_id_none_defaults_to_allowed_for_read_access(db_session, researcher_user):
    assert check_study_access(None, researcher_user, db_session) is True

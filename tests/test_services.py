from services.activity_log_service import ActivityLogService
from services.admin_user_service import AdminUserService
from services.applicant_service import ApplicantService
from services.client_service import ClientService
from services.hiring_status_service import HiringStatusService
from services.interview_service import InterviewService
from services.job_order_service import JobOrderService
from models.organization import Organization, OrganizationStatus
from services.seed_admin import seed_admin_user
from tests.helpers import build_test_session
from utils.passwords import hash_password, verify_password


def test_crud_services_and_admin_seed(tmp_path) -> None:
    session = build_test_session(tmp_path / "services_test.db")

    organization = Organization(
        name="Greater Connections Staffing",
        legal_name="Greater Connections Staffing LLC",
        status=OrganizationStatus.ACTIVE,
    )
    session.add(organization)
    session.commit()

    client_service = ClientService(session=session)
    client = client_service.create(
        organization_id=organization.id,
        company_name="Acme Corp",
        contact_name="Sam",
    )

    job_order_service = JobOrderService(session=session)
    job_order = job_order_service.create(
        organization_id=organization.id,
        client_id=client.id,
        job_code="ACME-PY-2026-001",
        title="Python Engineer",
    )

    applicant_service = ApplicantService(session=session)
    applicant = applicant_service.create(
        organization_id=organization.id,
        client_id=client.id,
        job_order_id=job_order.id,
        name="Jane Doe",
        email="jane@example.com",
        phone="555-1234",
    )
    applicant = applicant_service.update(applicant.id, current_status="Reviewed")
    assert applicant.current_status == "Reviewed"

    interview_service = InterviewService(session=session)
    interview = interview_service.create(
        applicant_id=applicant.id,
        job_order_id=job_order.id,
        interview_type="phone",
    )
    assert interview.interview_type == "phone"

    hiring_status_service = HiringStatusService(session=session)
    hiring_status = hiring_status_service.create(
        applicant_id=applicant.id,
        job_order_id=job_order.id,
        status="Screened",
    )
    assert hiring_status.status == "Screened"

    activity_log_service = ActivityLogService(session=session)
    activity_log = activity_log_service.create(
        entity_type="applicant",
        entity_id=applicant.id,
        action="created",
    )
    assert activity_log.action == "created"

    admin_user_service = AdminUserService(session=session)
    admin_user = admin_user_service.create(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("strong-password-123"),
        is_active=True,
    )
    assert admin_user.username == "admin"
    assert verify_password("strong-password-123", admin_user.password_hash) is True

    seeded_admin = seed_admin_user(session=session, username="bootstrap-admin", password="another-strong-pass")
    assert seeded_admin.username == "admin"

    assert applicant_service.delete(applicant.id) is True
    assert client_service.delete(client.id) is True
    session.close()

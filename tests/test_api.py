import os
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

TEST_DB = Path(__file__).with_name("test_payments.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["APP_SECRET"] = "test-secret"

from app.database import Base, SessionLocal, engine
from app.main import create_payment, dashboard, login, update_payment
from app.models import PaymentStatus, Role, User
from app.schemas import LoginRequest, PaymentCreate, PaymentUpdate
from app.seed import seed_database


def test_role_scoped_payment_flow():
    if TEST_DB.exists():
        TEST_DB.unlink()
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_database(db)
        client_user = db.scalar(select(User).where(User.role == Role.CLIENT))
        operator_user = db.scalar(select(User).where(User.role == Role.OPERATOR))

        session = login(LoginRequest(email="cliente@pagoclaro.co", password="Cliente123!"), db)
        assert session.user.role == Role.CLIENT

        created = create_payment(
            PaymentCreate(
                concept="Vacuna inicial",
                recipient="Clínica Central",
                amount=Decimal("54000"),
                currency="COP",
            ),
            client_user,
            db,
        )
        assert created.status == PaymentStatus.PENDING
        assert created.owner_id == client_user.id

        updated = update_payment(
            created.id,
            PaymentUpdate(status=PaymentStatus.APPROVED, note="Soporte verificado"),
            operator_user,
            db,
        )
        assert updated.status == PaymentStatus.APPROVED

        client_dashboard = dashboard(client_user, db)
        assert client_dashboard.approved_payments >= 2
        assert client_dashboard.total_approved_amount >= Decimal("234000")


def teardown_module():
    engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()


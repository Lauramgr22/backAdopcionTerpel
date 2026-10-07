from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Payment, PaymentStatus, Role, User
from .security import hash_password


DEMO_USERS = [
    ("Ana Administradora", "admin@pagoclaro.co", "Admin123!", Role.ADMIN),
    ("Óscar Operador", "operador@pagoclaro.co", "Operador123!", Role.OPERATOR),
    ("Clara Cliente", "cliente@pagoclaro.co", "Cliente123!", Role.CLIENT),
]


def seed_database(db: Session) -> None:
    if db.scalar(select(User.id).limit(1)):
        legacy_emails = {
            "admin@pago.local": "admin@pagoclaro.co",
            "operador@pago.local": "operador@pagoclaro.co",
            "cliente@pago.local": "cliente@pagoclaro.co",
        }
        for old_email, new_email in legacy_emails.items():
            user = db.scalar(select(User).where(User.email == old_email))
            if user:
                user.email = new_email
        db.commit()
        return

    users = []
    for name, email, password, role in DEMO_USERS:
        user = User(name=name, email=email, password_hash=hash_password(password), role=role)
        db.add(user)
        users.append(user)
    db.flush()

    payments = [
        Payment(reference="PAG-1001", concept="Cuota de adopción", recipient="Fundación Huellas", amount=Decimal("180000"), status=PaymentStatus.APPROVED, owner_id=users[2].id),
        Payment(reference="PAG-1002", concept="Valoración veterinaria", recipient="Clínica Buen Amigo", amount=Decimal("95000"), status=PaymentStatus.PENDING, owner_id=users[2].id),
        Payment(reference="PAG-1003", concept="Kit de bienvenida", recipient="Tienda Patitas", amount=Decimal("72000"), status=PaymentStatus.PROCESSING, owner_id=users[2].id),
    ]
    db.add_all(payments)
    db.commit()


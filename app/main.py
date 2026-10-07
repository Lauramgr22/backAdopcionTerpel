from contextlib import asynccontextmanager
from decimal import Decimal
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from .config import get_settings
from .database import Base, SessionLocal, engine, get_db
from .models import Payment, PaymentStatus, Role, User
from .schemas import DashboardResponse, LoginRequest, LoginResponse, PaymentCreate, PaymentUpdate, PaymentView
from .security import create_access_token, get_current_user, require_roles, verify_password
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


settings = get_settings()
local_origins = {settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"}

app = FastAPI(
    title="PagoClaro API",
    description="API local para el portal de pagos PagoClaro.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(local_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


def visible_payments_query(user: User):
    statement = select(Payment).options(joinedload(Payment.owner))
    if user.role == Role.CLIENT:
        statement = statement.where(Payment.owner_id == user.id)
    return statement


@app.post("/api/auth/login", response_model=LoginResponse, tags=["Autenticación"])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos")
    return LoginResponse(access_token=create_access_token(user), user=user)


@app.get("/api/dashboard", response_model=DashboardResponse, tags=["Portal"])
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payments = list(db.scalars(visible_payments_query(user).order_by(Payment.created_at.desc())).unique())
    approved = [payment for payment in payments if payment.status == PaymentStatus.APPROVED]
    return DashboardResponse(
        role=user.role,
        total_payments=len(payments),
        pending_payments=sum(payment.status in {PaymentStatus.PENDING, PaymentStatus.PROCESSING} for payment in payments),
        approved_payments=len(approved),
        total_approved_amount=sum((payment.amount for payment in approved), Decimal("0")),
        recent_payments=payments[:5],
    )


@app.get("/api/payments", response_model=list[PaymentView], tags=["Pagos"])
def list_payments(
    payment_status: PaymentStatus | None = Query(default=None, alias="status"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = visible_payments_query(user)
    if payment_status:
        statement = statement.where(Payment.status == payment_status)
    return list(db.scalars(statement.order_by(Payment.created_at.desc())).unique())


@app.post("/api/payments", response_model=PaymentView, status_code=status.HTTP_201_CREATED, tags=["Pagos"])
def create_payment(
    payload: PaymentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owner = user
    if payload.client_email and user.role != Role.CLIENT:
        owner = db.scalar(select(User).where(func.lower(User.email) == payload.client_email.lower(), User.role == Role.CLIENT))
        if not owner:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
    payment = Payment(
        reference=f"PAG-{uuid4().hex[:8].upper()}",
        concept=payload.concept.strip(),
        recipient=payload.recipient.strip(),
        amount=payload.amount,
        currency=payload.currency,
        status=PaymentStatus.PENDING,
        owner_id=owner.id,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return db.scalar(select(Payment).options(joinedload(Payment.owner)).where(Payment.id == payment.id))


@app.patch("/api/payments/{payment_id}", response_model=PaymentView, tags=["Pagos"])
def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    user: User = Depends(require_roles(Role.ADMIN, Role.OPERATOR)),
    db: Session = Depends(get_db),
):
    payment = db.scalar(select(Payment).options(joinedload(Payment.owner)).where(Payment.id == payment_id))
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    allowed = {
        Role.ADMIN: set(PaymentStatus),
        Role.OPERATOR: {PaymentStatus.PROCESSING, PaymentStatus.APPROVED, PaymentStatus.REJECTED},
    }
    if payload.status not in allowed[user.role]:
        raise HTTPException(status_code=403, detail="Transición no permitida para tu rol")
    payment.status = payload.status
    payment.note = payload.note
    db.commit()
    db.refresh(payment)
    return payment


from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import PaymentStatus, Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserView(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserView


class PaymentCreate(BaseModel):
    concept: str = Field(min_length=3, max_length=160)
    recipient: str = Field(min_length=3, max_length=160)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="COP", pattern="^[A-Z]{3}$")
    client_email: EmailStr | None = None


class PaymentUpdate(BaseModel):
    status: PaymentStatus
    note: str | None = Field(default=None, max_length=500)


class PaymentView(BaseModel):
    id: int
    reference: str
    concept: str
    recipient: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    note: str | None
    owner: UserView
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    role: Role
    total_payments: int
    pending_payments: int
    approved_payments: int
    total_approved_amount: Decimal
    recent_payments: list[PaymentView]


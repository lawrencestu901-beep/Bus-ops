from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import BusStatus, TrafficLevel, TransactionType, TripStatus, UserRole


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class UserRegister(BaseModel):
    name: str
    phone: str
    password: str = Field(min_length=6)
    role: UserRole = UserRole.passenger


class UserLogin(BaseModel):
    phone: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    role: UserRole
    wallet_balance: float
    home_place: Optional[str] = None
    work_place: Optional[str] = None
    created_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = None
    home_place: Optional[str] = None
    work_place: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


# ---------------------------------------------------------------------------
# Stop
# ---------------------------------------------------------------------------
class StopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    name: str
    x: float
    y: float


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------
class RouteStopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: int
    stop: StopRead


class RouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_no: str
    via: str
    fare: float
    minutes: int
    traffic: TrafficLevel
    stops: list[RouteStopRead] = []


# ---------------------------------------------------------------------------
# Bus
# ---------------------------------------------------------------------------
class BusRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bus_no: str
    plate_no: Optional[str] = None
    route_id: Optional[int] = None
    driver_id: Optional[int] = None
    status: BusStatus
    seats_total: int
    seats_available: int
    fuel_level: float
    current_stop_key: Optional[str] = None
    color: Optional[str] = None


# ---------------------------------------------------------------------------
# Trip planning (route-finder results — not a booked trip yet)
# ---------------------------------------------------------------------------
class TripOptionRead(BaseModel):
    id: str
    route: str
    via: str
    fare: float
    mins: int
    km: Optional[float] = None
    traffic: str
    recommended: bool
    transfer: bool
    transfer_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Trip (booked journey)
# ---------------------------------------------------------------------------
class TripCreate(BaseModel):
    from_stop_key: str
    to_stop_key: str
    route_id: Optional[int] = None
    bus_id: Optional[int] = None
    fare: float


class TripRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    from_stop_id: int
    to_stop_id: int
    route_id: Optional[int] = None
    bus_id: Optional[int] = None
    fare: float
    status: TripStatus
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Wallet
# ---------------------------------------------------------------------------
class WalletTopUp(BaseModel):
    amount: float = Field(gt=0)
    label: str = "Top-up"


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: TransactionType
    label: str
    amount: float
    created_at: datetime


# ---------------------------------------------------------------------------
# Rating
# ---------------------------------------------------------------------------
class RatingCreate(BaseModel):
    trip_id: int
    stars: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class RatingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    stars: int
    comment: Optional[str] = None
    created_at: datetime

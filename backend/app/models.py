import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    passenger = "passenger"
    driver = "driver"
    admin = "admin"


class TrafficLevel(str, enum.Enum):
    Low = "Low"
    Moderate = "Moderate"
    Heavy = "Heavy"


class BusStatus(str, enum.Enum):
    on_route = "On Route"
    delayed = "Delayed"
    maintenance = "Maintenance"
    offline = "Offline"


class TripStatus(str, enum.Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class TransactionType(str, enum.Enum):
    topup = "topup"
    trip = "trip"
    refund = "refund"


# ---------------------------------------------------------------------------
# Users (passengers, drivers, admins/operators all share one table + role)
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.passenger, nullable=False)
    wallet_balance = Column(Float, default=0.0, nullable=False)
    home_place = Column(String(120), nullable=True)   # "Favorites: Home"
    work_place = Column(String(120), nullable=True)   # "Favorites: Work"
    emergency_contact_name = Column(String(120), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="user", foreign_keys="Trip.user_id")
    transactions = relationship("WalletTransaction", back_populates="user")
    ratings = relationship("Rating", back_populates="user")
    driven_buses = relationship("Bus", back_populates="driver")


# ---------------------------------------------------------------------------
# Stops
# ---------------------------------------------------------------------------
class Stop(Base):
    __tablename__ = "stops"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, index=True, nullable=False)  # e.g. "town_centre"
    name = Column(String(120), nullable=False)                         # e.g. "Town Centre Market"
    x = Column(Float, nullable=False)  # mock-map coordinate (0-100)
    y = Column(Float, nullable=False)  # mock-map coordinate (0-100)
    aliases = Column(Text, nullable=True)  # comma-separated search aliases

    route_links = relationship("RouteStop", back_populates="stop")


# ---------------------------------------------------------------------------
# Routes + ordered stops on each route
# ---------------------------------------------------------------------------
class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    route_no = Column(String(10), unique=True, index=True, nullable=False)  # "125"
    via = Column(String(120), nullable=False)                               # "Great East Road"
    fare = Column(Float, nullable=False)
    minutes = Column(Integer, nullable=False)
    traffic = Column(Enum(TrafficLevel), default=TrafficLevel.Low)

    stops = relationship(
        "RouteStop", back_populates="route", order_by="RouteStop.position",
        cascade="all, delete-orphan",
    )
    buses = relationship("Bus", back_populates="route")


class RouteStop(Base):
    """Join table giving each route an ORDERED list of stops."""
    __tablename__ = "route_stops"
    __table_args__ = (UniqueConstraint("route_id", "position", name="uq_route_position"),)

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    stop_id = Column(Integer, ForeignKey("stops.id"), nullable=False)
    position = Column(Integer, nullable=False)  # 0, 1, 2... order along the route

    route = relationship("Route", back_populates="stops")
    stop = relationship("Stop", back_populates="route_links")


# ---------------------------------------------------------------------------
# Buses (fleet) — used by both the passenger app's "nearby buses" and the
# operator dashboard's live tracking / fleet status views
# ---------------------------------------------------------------------------
class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    bus_no = Column(String(10), unique=True, index=True, nullable=False)  # "125"
    plate_no = Column(String(20), nullable=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(BusStatus), default=BusStatus.on_route)
    seats_total = Column(Integer, default=45)
    seats_available = Column(Integer, default=45)
    fuel_level = Column(Float, default=100.0)  # percent
    current_stop_key = Column(String(50), nullable=True)  # for live-position mocking
    color = Column(String(20), nullable=True)  # hex, for map markers

    route = relationship("Route", back_populates="buses")
    driver = relationship("User", back_populates="driven_buses")
    trips = relationship("Trip", back_populates="bus")


# ---------------------------------------------------------------------------
# Trips (a passenger's planned/active/completed journey)
# ---------------------------------------------------------------------------
class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    from_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=False)
    to_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=True)
    fare = Column(Float, nullable=False)
    status = Column(Enum(TripStatus), default=TripStatus.planned)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trips", foreign_keys=[user_id])
    from_stop = relationship("Stop", foreign_keys=[from_stop_id])
    to_stop = relationship("Stop", foreign_keys=[to_stop_id])
    route = relationship("Route")
    bus = relationship("Bus", back_populates="trips")
    rating = relationship("Rating", back_populates="trip", uselist=False)


# ---------------------------------------------------------------------------
# Wallet transactions
# ---------------------------------------------------------------------------
class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    label = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)  # positive = topup/refund, negative = trip spend
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


# ---------------------------------------------------------------------------
# Ratings
# ---------------------------------------------------------------------------
class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stars = Column(Integer, nullable=False)  # 1-5
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="rating")
    user = relationship("User", back_populates="ratings")


# ---------------------------------------------------------------------------
# Promo codes
# ---------------------------------------------------------------------------
class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, index=True, nullable=False)
    percent = Column(Integer, nullable=False)
    label = Column(String(200), nullable=False)
    active = Column(Boolean, default=True)

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Stop, Trip, TripStatus, User, WalletTransaction
from app.models import TransactionType
from app.schemas import TripCreate, TripOptionRead, TripRead
from app.trip_planner import plan_trip, resolve_stop

router = APIRouter(tags=["trips"])


@router.get("/trip-planner", response_model=list[TripOptionRead])
def plan(
    from_: str = Query(..., alias="from", description="Stop key or free text, e.g. 'kulima'"),
    to: str = Query(..., description="Stop key or free text"),
    db: Session = Depends(get_db),
):
    """Mirrors the frontend's planTrip(): resolves free-text stop names,
    then returns direct routes if any exist, else up to 3 transfer options."""
    from_stop = resolve_stop(db, from_)
    to_stop = resolve_stop(db, to)
    if not from_stop:
        raise HTTPException(status_code=404, detail=f"Could not find a stop matching '{from_}'")
    if not to_stop:
        raise HTTPException(status_code=404, detail=f"Could not find a stop matching '{to}'")
    if from_stop.id == to_stop.id:
        raise HTTPException(status_code=400, detail="Origin and destination are the same stop")

    return plan_trip(db, from_stop.key, to_stop.key)


@router.post("/trips", response_model=TripRead, status_code=status.HTTP_201_CREATED)
def book_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Books a trip: validates stops, charges the fare from the wallet,
    and creates the trip in 'planned' status. Fails with 402 if the
    wallet balance can't cover the fare."""
    from_stop = db.query(Stop).filter(Stop.key == payload.from_stop_key).first()
    to_stop = db.query(Stop).filter(Stop.key == payload.to_stop_key).first()
    if not from_stop or not to_stop:
        raise HTTPException(status_code=404, detail="Unknown from_stop_key or to_stop_key")

    if current_user.wallet_balance < payload.fare:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient wallet balance: have {current_user.wallet_balance}, need {payload.fare}",
        )

    trip = Trip(
        user_id=current_user.id,
        from_stop_id=from_stop.id,
        to_stop_id=to_stop.id,
        route_id=payload.route_id,
        bus_id=payload.bus_id,
        fare=payload.fare,
        status=TripStatus.planned,
    )
    db.add(trip)

    current_user.wallet_balance -= payload.fare
    db.add(
        WalletTransaction(
            user_id=current_user.id,
            type=TransactionType.trip,
            label=f"Trip: {from_stop.name} → {to_stop.name}",
            amount=-payload.fare,
        )
    )

    db.commit()
    db.refresh(trip)
    return trip


@router.get("/trips", response_model=list[TripRead])
def list_my_trips(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return (
        db.query(Trip)
        .filter(Trip.user_id == current_user.id)
        .order_by(Trip.created_at.desc())
        .all()
    )


@router.get("/trips/{trip_id}", response_model=TripRead)
def get_trip(
    trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    trip = _get_owned_trip(db, trip_id, current_user)
    return trip


@router.patch("/trips/{trip_id}/start", response_model=TripRead)
def start_trip(
    trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    trip = _get_owned_trip(db, trip_id, current_user)
    if trip.status != TripStatus.planned:
        raise HTTPException(status_code=400, detail=f"Trip is '{trip.status.value}', cannot start it")
    trip.status = TripStatus.active
    trip.started_at = datetime.utcnow()
    db.commit()
    db.refresh(trip)
    return trip


@router.patch("/trips/{trip_id}/complete", response_model=TripRead)
def complete_trip(
    trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    trip = _get_owned_trip(db, trip_id, current_user)
    if trip.status != TripStatus.active:
        raise HTTPException(status_code=400, detail=f"Trip is '{trip.status.value}', cannot complete it")
    trip.status = TripStatus.completed
    trip.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(trip)
    return trip


@router.patch("/trips/{trip_id}/cancel", response_model=TripRead)
def cancel_trip(
    trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Cancels a planned trip and refunds the fare to the wallet."""
    trip = _get_owned_trip(db, trip_id, current_user)
    if trip.status != TripStatus.planned:
        raise HTTPException(status_code=400, detail=f"Trip is '{trip.status.value}', cannot cancel it")
    trip.status = TripStatus.cancelled
    current_user.wallet_balance += trip.fare
    db.add(
        WalletTransaction(
            user_id=current_user.id,
            type=TransactionType.refund,
            label=f"Refund: cancelled trip #{trip.id}",
            amount=trip.fare,
        )
    )
    db.commit()
    db.refresh(trip)
    return trip


def _get_owned_trip(db: Session, trip_id: int, current_user: User) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your trip")
    return trip

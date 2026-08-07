from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Rating, Trip, TripStatus, User
from app.schemas import RatingCreate, RatingRead

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("", response_model=RatingRead, status_code=status.HTTP_201_CREATED)
def rate_trip(
    payload: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == payload.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your trip")
    if trip.status != TripStatus.completed:
        raise HTTPException(status_code=400, detail="Only completed trips can be rated")
    if db.query(Rating).filter(Rating.trip_id == trip.id).first():
        raise HTTPException(status_code=400, detail="Trip already rated")

    rating = Rating(
        trip_id=trip.id,
        user_id=current_user.id,
        stars=payload.stars,
        comment=payload.comment,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


@router.get("/my", response_model=list[RatingRead])
def my_ratings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Rating).filter(Rating.user_id == current_user.id).all()

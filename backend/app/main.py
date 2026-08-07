from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import Base, engine, get_db
from app.models import Bus, Route, Stop, User
from app.routers_ratings import router as ratings_router
from app.routers_trips import router as trips_router
from app.routers_wallet import router as wallet_router
from app.schemas import BusRead, RouteRead, StopRead, Token, UserLogin, UserRead, UserRegister

# Week 2 will move this to Alembic migrations; for now, create tables on boot.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lusaka Bus AI API", version="0.1.0")

# Wide open for local dev / Week 3 frontend wiring. Tighten before production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trips_router)
app.include_router(wallet_router)
app.include_router(ratings_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    user = User(
        name=payload.name,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect phone or password")
    token = create_access_token(user.id)
    return Token(access_token=token)


@app.get("/auth/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ---------------------------------------------------------------------------
# Read-only endpoints — prove the seed data loaded, and give the frontends
# something real to switch to in Week 3.
# ---------------------------------------------------------------------------
@app.get("/stops", response_model=list[StopRead])
def list_stops(db: Session = Depends(get_db)):
    return db.query(Stop).all()


@app.get("/routes", response_model=list[RouteRead])
def list_routes(db: Session = Depends(get_db)):
    return db.query(Route).all()


@app.get("/buses", response_model=list[BusRead])
def list_buses(db: Session = Depends(get_db)):
    return db.query(Bus).all()

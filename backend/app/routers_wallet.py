from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import TransactionType, User, WalletTransaction
from app.schemas import TransactionRead, UserRead, WalletTopUp

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/balance", response_model=UserRead)
def get_balance(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/topup", response_model=UserRead)
def top_up(
    payload: WalletTopUp,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.wallet_balance += payload.amount
    db.add(
        WalletTransaction(
            user_id=current_user.id,
            type=TransactionType.topup,
            label=payload.label,
            amount=payload.amount,
        )
    )
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/transactions", response_model=list[TransactionRead])
def list_transactions(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return (
        db.query(WalletTransaction)
        .filter(WalletTransaction.user_id == current_user.id)
        .order_by(WalletTransaction.created_at.desc())
        .all()
    )

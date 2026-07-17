from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import SiteSetting

router = APIRouter(tags=["Storefront"])


@router.get("/settings")
def settings(db: Session = Depends(get_db)):
    return {item.key: item.value for item in db.scalars(select(SiteSetting)).all()}

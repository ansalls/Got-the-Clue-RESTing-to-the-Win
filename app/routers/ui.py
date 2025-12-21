from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db


router = APIRouter(tags=["UI"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/ui", response_class=HTMLResponse)
def ui_home(request: Request, db: Session = Depends(get_db)):
    games = db.query(models.Game).order_by(models.Game.created_at.desc()).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "games": games},
    )


@router.post("/ui/games")
def ui_create_game(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    trimmed_name = name.strip()
    if not trimmed_name:
        games = db.query(models.Game).order_by(models.Game.created_at.desc()).all()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "games": games,
                "error": "Game name cannot be empty.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    new_game = models.Game(name=trimmed_name)
    db.add(new_game)
    db.commit()
    return RedirectResponse(url="/ui", status_code=status.HTTP_303_SEE_OTHER)

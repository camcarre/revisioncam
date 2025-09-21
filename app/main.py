from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, SessionLocal, engine
from .initial_data import ensure_defaults
from .routers import bareme, cours, disponibilites, examens, parametres, planning, scores

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        ensure_defaults(session)
    yield


app = FastAPI(title="Planning de révisions", lifespan=lifespan)

app.include_router(examens.router, prefix="/examens", tags=["examens"])
app.include_router(cours.router, prefix="/cours", tags=["cours"])
app.include_router(planning.router, prefix="/planning", tags=["planning"])
app.include_router(scores.router, prefix="/scores", tags=["scores"])
app.include_router(parametres.router, prefix="/parametres", tags=["parametres"])
app.include_router(bareme.router, prefix="/bareme", tags=["bareme"])
app.include_router(disponibilites.router, prefix="/disponibilite", tags=["disponibilite"])

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

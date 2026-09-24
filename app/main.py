from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import auth, documents, ocr, ai


app = FastAPI(
    title="WorkFlow AI",
    description="API para gerenciamento, OCR e análise de documentos com IA",
    version="1.0.0"
)


# =========================
# ROTAS DA API
# =========================

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(ocr.router)
app.include_router(ai.router)


# =========================
# FRONTEND
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount(
    "/css",
    StaticFiles(directory=FRONTEND_DIR / "css"),
    name="css"
)

app.mount(
    "/js",
    StaticFiles(directory=FRONTEND_DIR / "js"),
    name="js"
)


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/dashboard.html", include_in_schema=False)
def dashboard():
    return FileResponse(FRONTEND_DIR / "dashboard.html")
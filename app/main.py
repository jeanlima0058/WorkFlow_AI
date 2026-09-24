from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.routes.auth import router as auth_router
from app.routes.documents import router as documents_router
from app.routes.ocr import router as ocr_router
from app.routes.ai import router as ai_router
from app.routes.admin import router as admin_router # NOVO

app = FastAPI(title="WorkFlow AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"], # Adicione a URL do Render se necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos do frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

# Rotas da API
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(ocr_router)
app.include_router(ai_router)
app.include_router(admin_router) # NOVO

# Rotas para servir o frontend
@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/dashboard.html", include_in_schema=False)
def dashboard():
    return FileResponse(FRONTEND_DIR / "dashboard.html")

@app.get("/admin.html", include_in_schema=False) # NOVO
def admin_page():
    return FileResponse(FRONTEND_DIR / "admin.html")
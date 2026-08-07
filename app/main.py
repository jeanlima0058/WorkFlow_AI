from fastapi import FastAPI


app = FastAPI(
    title="DocFlow AI",
    version="1.0.0",
    description="API para automação inteligente de recepção e processamento de documentos."
)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "DocFlow AI API funcionando"
    }
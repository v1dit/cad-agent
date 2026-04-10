from fastapi import FastAPI

from app.routes.pipeline import router

app = FastAPI(title="cad-agent")
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "cad-agent running"}

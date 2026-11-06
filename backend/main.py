from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.audit_logger import audit_logger
from app.core.config import settings
from app.services.sentinel_agent import sentinel_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    audit_logger.record(
        stage="AGENT_REASONING",
        actor="SentinelPayBoot",
        summary="SentinelPay AI Agentic Commerce Engine started (PayPal Sandbox + Gemini Ready)",
        details={"version": "1.0.0"},
    )
    sentinel_agent.synchronize_audit_and_proposals()
    yield


app = FastAPI(
    title="SentinelPay AI — Autonomous Agentic Commerce API",
    description=(
        "Autonomous Financial Agent powered by PayPal Sandbox REST APIs "
        "(Subscriptions v1, Catalogs v1, Orders v2) & Google Gemini AI."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "SentinelPay AI Backend"}

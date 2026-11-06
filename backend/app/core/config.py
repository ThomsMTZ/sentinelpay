import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root or backend directory
ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]

load_dotenv(ROOT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env")


def mask_secret(value: str | None) -> str | None:
    """Masks sensitive credentials so only the first/last 4 chars are visible."""
    if not value:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if len(cleaned) > 8:
        return f"{cleaned[:4]}••••{cleaned[-4:]}"
    return "••••••••"


def _sanitize_credential(value: str) -> str:
    if any(ch in value for ch in ("\n", "\r", "\x00")):
        raise ValueError("Invalid control characters in credentials")
    return value.strip()


class AppConfig:
    """Centralized runtime configuration with hot-reload support for API credentials."""

    def __init__(self) -> None:
        self.paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "").strip()
        self.paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "").strip()
        self.paypal_base_url: str = os.getenv(
            "PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com"
        ).strip()
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.default_monthly_budget_limit: float = float(
            os.getenv("DEFAULT_MONTHLY_BUDGET_LIMIT", "150.00")
        )
        self.default_auto_approve_threshold: float = float(
            os.getenv("DEFAULT_AUTO_APPROVE_THRESHOLD", "25.00")
        )
        self.default_currency: str = os.getenv("DEFAULT_CURRENCY", "USD").strip()
        self.allowed_origins: list[str] = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    @property
    def is_paypal_live_sandbox_configured(self) -> bool:
        return bool(self.paypal_client_id and self.paypal_client_secret)

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

    def update_credentials(
        self,
        paypal_client_id: str | None = None,
        paypal_client_secret: str | None = None,
        gemini_api_key: str | None = None,
        gemini_model: str | None = None,
    ) -> None:
        """Dynamically updates runtime credentials and persists them to root .env."""
        for candidate in (paypal_client_id, paypal_client_secret, gemini_api_key, gemini_model):
            if candidate is not None:
                _sanitize_credential(candidate)

        if paypal_client_id is not None:
            self.paypal_client_id = _sanitize_credential(paypal_client_id)
        if paypal_client_secret is not None:
            self.paypal_client_secret = _sanitize_credential(paypal_client_secret)
        if gemini_api_key is not None:
            self.gemini_api_key = _sanitize_credential(gemini_api_key)
        if gemini_model is not None and gemini_model.strip():
            self.gemini_model = _sanitize_credential(gemini_model)

        env_path = ROOT_DIR / ".env"
        env_content = (
            f"PAYPAL_CLIENT_ID={self.paypal_client_id}\n"
            f"PAYPAL_CLIENT_SECRET={self.paypal_client_secret}\n"
            f"PAYPAL_BASE_URL={self.paypal_base_url}\n"
            f"PAYPAL_MODE=sandbox\n"
            f"GEMINI_API_KEY={self.gemini_api_key}\n"
            f"GEMINI_MODEL={self.gemini_model}\n"
            f"DEFAULT_MONTHLY_BUDGET_LIMIT={self.default_monthly_budget_limit}\n"
            f"DEFAULT_AUTO_APPROVE_THRESHOLD={self.default_auto_approve_threshold}\n"
            f"DEFAULT_CURRENCY={self.default_currency}\n"
        )
        try:
            env_path.write_text(env_content, encoding="utf-8")
        except OSError:
            pass


settings = AppConfig()

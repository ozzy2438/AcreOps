from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    acreops_env: str = "demo"
    acreops_api_host: str = "0.0.0.0"
    acreops_api_port: int = 8000
    acreops_data_dir: Path = Path("data")
    acreops_artifact_dir: Path = Path("artifacts")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llama_base_url: str = ""
    llama_model: str = "llama-3.1-70b-instruct"

    pandadoc_api_key: str = ""
    pandadoc_template_uuid: str = ""

    appfolio_webhook_secret: str = ""
    airtable_api_key: str = ""
    airtable_base_id: str = ""
    airtable_vendors_table: str = "Vendors"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    permit_alert_email: str = "pm@acreops.local"
    notion_api_key: str = ""
    notion_timeline_database_id: str = ""

    openai_vision_model: str = "gpt-4o-mini"
    churn_model_path: Path = Path("artifacts/churn_lightgbm.txt")
    churn_from_email: str = "renewals@acreops.local"

    @property
    def demo_mode(self) -> bool:
        return self.acreops_env == "demo" or not self.openai_api_key

    @property
    def has_llm(self) -> bool:
        return bool(self.openai_api_key or self.llama_base_url)


def get_settings() -> Settings:
    return Settings()

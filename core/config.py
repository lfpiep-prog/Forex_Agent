from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class Settings(BaseSettings):
    # IG Markets
    IG_USERNAME: str = Field(..., description="IG Markets Username")
    IG_PASSWORD: str = Field(..., description="IG Markets Password")
    IG_API_KEY: str = Field(..., description="IG Markets API Key")
    IG_ACC_TYPE: str = Field("DEMO", description="Account Type: DEMO or LIVE")

    # APIs
    BRAVE_API_KEY: str | None = Field(None, description="Brave Search API Key")
    TWELVEDATA_API_KEY: str | None = Field(None, description="TwelveData API Key")

    @field_validator("IG_ACC_TYPE")
    @classmethod
    def validate_acc_type(cls, v: str) -> str:
        v = v.upper()
        if v not in ("DEMO", "LIVE"):
            raise ValueError("IG_ACC_TYPE must be 'DEMO' or 'LIVE'")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars

settings = Settings()

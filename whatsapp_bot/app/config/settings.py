"""Application settings and configuration."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # WhatsApp Business API Configuration
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID", "")
    VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN", "")
    GRAPH_API_VERSION: str = os.getenv("GRAPH_API_VERSION", "v20.0")
    
    # External API Configuration
    EXTERNAL_API_URL: str = os.getenv("EXTERNAL_API_URL")
    
    # Database API Configuration
    DATABASE_API_URL: str = os.getenv("DATABASE_API_URL")
    DATABASE_API_TOKEN: str = os.getenv("DATABASE_API_TOKEN")

    # API URLs
    @property
    def GRAPH_URL(self) -> str:
        """WhatsApp Graph API URL."""
        return f"https://graph.facebook.com/{self.GRAPH_API_VERSION}/{self.PHONE_NUMBER_ID}/messages"
    
    @property
    def HEADERS(self) -> dict:
        """Headers for WhatsApp API requests."""
        return {
            "Authorization": f"Bearer {self.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def validate(self) -> None:
        """Validate that all required settings are present."""
        required_vars = [
            ("WHATSAPP_TOKEN", self.WHATSAPP_TOKEN),
            ("PHONE_NUMBER_ID", self.PHONE_NUMBER_ID),
            ("VERIFY_TOKEN", self.VERIFY_TOKEN)
        ]
        
        missing = [name for name, value in required_vars if not value]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


# Global settings instance
settings = Settings()

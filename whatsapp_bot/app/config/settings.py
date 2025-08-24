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
    EXTERNAL_API_URL: str = os.getenv("EXTERNAL_API_URL", "https://api.example.com/process")
    
    # Database API Configuration
    DATABASE_API_URL: str = os.getenv("DATABASE_API_URL", "http://18.190.66.49:8000/api/patients/intake/")
    DATABASE_API_TOKEN: str = os.getenv("DATABASE_API_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU1OTk4ODU3LCJpYXQiOjE3NTU5OTUyNTcsImp0aSI6ImY4ODg0Yjc5ZmEyMjRiZmFhNzE4YTU5N2JkN2U2NDE0IiwidXNlcl9pZCI6IjMifQ.wHRimBdpxeriYqI7tKVYN7ruzKEUhRn-sKBiaMUCKWA")
    
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

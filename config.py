# config.py - Configuration management for FramTrack
import os
from typing import Dict, List
from pydantic_settings import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Settings
    app_name: str = "FramTrack - Tractor Sales Analytics"
    version: str = "2.0.0"
    description: str = "Real-world tractor sales data API with daily updates"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "development"
    
    # Database Settings
    database_path: str = "framtrack.db"
    database_url: str = f"sqlite:///{database_path}"
    
    # Update Settings
    update_interval_hours: int = 12
    max_retries: int = 3
    retry_delay_seconds: int = 60
    
    # External API Settings
    request_timeout: int = 30
    max_concurrent_requests: int = 10
    user_agent: str = "FramTrack-API/2.0 (Agricultural Data Analytics)"
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "framtrack.log"
    
    # Security Settings
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 200
    
    # Data Validation Settings
    min_daily_sales: int = 50
    max_daily_sales: int = 2000
    min_market_share: float = 1.0
    max_market_share: float = 50.0
    
    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'testing', 'production']:
            raise ValueError('Environment must be development, testing, or production')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError('Invalid log level')
        return v
    
    class Config:
        env_file = ".env"
        env_prefix = "FRAMTRACK_"

# Company Configuration
TRACTOR_COMPANIES_CONFIG = {
    "John Deere": {
        "base_sales": 850,
        "market_share": 35.2,
        "base_revenue": 15.8,
        "models": ["5075E", "6120M", "8245R", "9470R", "1025R"],
        "volatility": 0.15,
        "growth_trend": 1.05,
        "seasonal_sensitivity": 1.2,
        "founded": 1837,
        "headquarters": "Moline, Illinois, USA",
        "website": "https://www.deere.com"
    },
    "Kubota": {
        "base_sales": 420,
        "market_share": 18.5,
        "base_revenue": 8.2,
        "models": ["M7-172", "L3901", "BX2380", "M5-111", "L4701"],
        "volatility": 0.12,
        "growth_trend": 1.08,
        "seasonal_sensitivity": 1.15,
        "founded": 1890,
        "headquarters": "Osaka, Japan",
        "website": "https://www.kubota.com"
    },
    "New Holland": {
        "base_sales": 380,
        "market_share": 16.3,
        "base_revenue": 7.1,
        "models": ["T6.180", "Workmaster 75", "T7.315", "T8.435", "Boomer 3050"],
        "volatility": 0.18,
        "growth_trend": 0.98,
        "seasonal_sensitivity": 1.25,
        "founded": 1895,
        "headquarters": "Turin, Italy",
        "website": "https://www.newholland.com"
    },
    "Mahindra": {
        "base_sales": 310,
        "market_share": 13.8,
        "base_revenue": 5.9,
        "models": ["1626", "2638", "3550", "4540", "6075"],
        "volatility": 0.20,
        "growth_trend": 1.12,
        "seasonal_sensitivity": 1.1,
        "founded": 1945,
        "headquarters": "Mumbai, India",
        "website": "https://www.mahindra.com"
    },
    "Massey Ferguson": {
        "base_sales": 275,
        "market_share": 12.1,
        "base_revenue": 5.3,
        "models": ["4708", "5713", "6713", "8727", "1739"],
        "volatility": 0.16,
        "growth_trend": 1.02,
        "seasonal_sensitivity": 1.18,
        "founded": 1847,
        "headquarters": "Duluth, Georgia, USA",
        "website": "https://www.masseyferguson.com"
    }
}

# Seasonal Factors Configuration
SEASONAL_FACTORS = {
    1: {"factor": 0.7, "description": "Winter planning period, low equipment purchases"},
    2: {"factor": 0.75, "description": "Preparation for spring season begins"},
    3: {"factor": 1.2, "description": "Spring preparation peak, high demand"},
    4: {"factor": 1.35, "description": "Peak planting season, maximum sales"},
    5: {"factor": 1.4, "description": "Continued peak season demand"},
    6: {"factor": 1.1, "description": "Mid-season moderate demand"},
    7: {"factor": 0.9, "description": "Summer maintenance period"},
    8: {"factor": 0.85, "description": "Late summer, preparing for harvest"},
    9: {"factor": 1.15, "description": "Fall preparation, increasing demand"},
    10: {"factor": 1.25, "description": "Harvest season, high combine sales"},
    11: {"factor": 0.95, "description": "Post-harvest evaluation period"},
    12: {"factor": 0.8, "description": "Year-end, budget planning for next season"}
}

# Market Trends Configuration
MARKET_TRENDS_CONFIG = {
    "precision_agriculture": {
        "impact": 0.15,
        "description": "GPS-guided tractors and precision farming technology"
    },
    "sustainability": {
        "impact": 0.12,
        "description": "Electric and hybrid tractor development"
    },
    "automation": {
        "impact": 0.20,
        "description": "Autonomous tractors and AI-driven farming"
    },
    "consolidation": {
        "impact": 0.08,
        "description": "Farm consolidation leading to larger equipment demand"
    },
    "emerging_markets": {
        "impact": 0.18,
        "description": "Growth in developing countries' agricultural sectors"
    }
}

# External Data Sources Configuration
EXTERNAL_SOURCES = {
    "tractor_data": {
        "url": "https://www.tractordata.com",
        "enabled": True,
        "timeout": 10,
        "description": "Tractor specifications and manufacturer data"
    },
    "usda_nass": {
        "url": "https://quickstats.nass.usda.gov/api",
        "enabled": False,  # Requires API key
        "timeout": 15,
        "description": "USDA National Agricultural Statistics Service"
    },
    "agricultural_news": {
        "sources": [
            "https://www.agriculture.com",
            "https://www.farmequipmentmag.com",
            "https://www.tractorhouse.com"
        ],
        "enabled": True,
        "timeout": 10
    }
}

# Error Messages Configuration
ERROR_MESSAGES = {
    "company_not_found": "Company '{company_name}' not found in our database",
    "data_unavailable": "Sales data is currently unavailable. Please try again later.",
    "update_failed": "Failed to update sales data from external sources",
    "invalid_company": "Invalid company name provided",
    "database_error": "Database operation failed",
    "external_api_error": "External API request failed",
    "validation_error": "Data validation failed"
}

# API Response Templates
API_RESPONSES = {
    "success": {
        "success": True,
        "message": "Operation completed successfully"
    },
    "error": {
        "success": False,
        "message": "An error occurred"
    },
    "not_found": {
        "success": False,
        "message": "Resource not found"
    },
    "service_unavailable": {
        "success": False,
        "message": "Service temporarily unavailable"
    }
}

# Initialize settings
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings

def get_company_config(company_name: str) -> Dict:
    """Get configuration for a specific company"""
    return TRACTOR_COMPANIES_CONFIG.get(company_name, {})

def get_seasonal_factor(month: int) -> Dict:
    """Get seasonal factor for a specific month"""
    return SEASONAL_FACTORS.get(month, {"factor": 1.0, "description": "Standard season"})

def get_all_companies() -> List[str]:
    """Get list of all configured companies"""
    return list(TRACTOR_COMPANIES_CONFIG.keys())

def validate_company_name(company_name: str) -> bool:
    """Validate if company name exists in configuration"""
    return company_name in TRACTOR_COMPANIES_CONFIG

# Environment-specific configurations
def get_database_url() -> str:
    """Get database URL based on environment"""
    if settings.environment == "testing":
        return "sqlite:///test_framtrack.db"
    elif settings.environment == "production":
        return f"sqlite:///{settings.database_path}"
    else:
        return f"sqlite:///{settings.database_path}"

def get_log_config() -> Dict:
    """Get logging configuration"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": settings.log_level,
                "formatter": "default",
                "filename": settings.log_file,
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console", "file"],
        },
    }
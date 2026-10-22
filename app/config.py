"""
app/config.py – Application configuration environments.

Psychometric Learning Analytics Framework (J26-DS-310)
Supports development, testing, and production environments.
"""

import os


class Config:
    """Base configuration with safe development defaults."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-key-j26-ds-310")
    TESTING = False
    DEBUG = False
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Development configuration for local testing and prototype runs."""

    DEBUG = True


class TestingConfig(Config):
    """Testing configuration for automated test suites."""

    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration for deployment."""

    DEBUG = False
    TESTING = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

"""Database package for Blackcrest Recruiting AI."""

from .base import Base
from .init_db import initialize_database

__all__ = ["Base", "initialize_database"]

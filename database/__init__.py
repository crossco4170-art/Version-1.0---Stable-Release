"""Database package for BlackcrestRecruitOS."""

from .base import Base
from .init_db import initialize_database

__all__ = ["Base", "initialize_database"]

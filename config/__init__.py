"""Configuration package for BlackcrestRecruitOS."""

from config.secrets import get_optional, get_required, validate_required
from config.settings import Settings, settings

__all__ = [
	"Settings",
	"settings",
	"get_required",
	"get_optional",
	"validate_required",
]

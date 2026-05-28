"""Shared Hatchet client instance."""
import os
from hatchet_sdk import Hatchet

hatchet = Hatchet(debug=os.getenv("DEBUG", "false").lower() == "true")

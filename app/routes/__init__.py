"""Routes package for the application."""
from routes.webhook_routes import (
    send_single_pdf,
    send_directory,
    send_year,
    send_all_years
)

__all__ = [
    "send_single_pdf",
    "send_directory", 
    "send_year",
    "send_all_years"
]

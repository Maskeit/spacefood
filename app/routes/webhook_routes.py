"""
Routes for webhook operations.
Provides CLI commands for sending PDFs to n8n webhook.
"""
from services.webhook_sender import WebhookSenderService


def send_single_pdf(pdf_path: str, webhook_url: str = None) -> dict:
    """
    Send a single PDF file to the webhook.
    
    Args:
        pdf_path: Path to the PDF file
        webhook_url: Optional custom webhook URL
        
    Returns:
        Result dictionary
    """
    service = WebhookSenderService(webhook_url)
    return service.send_pdf(pdf_path)


def send_directory(directory: str, webhook_url: str = None, recursive: bool = False) -> dict:
    """
    Send all PDFs from a directory to the webhook.
    
    Args:
        directory: Path to directory containing PDFs
        webhook_url: Optional custom webhook URL
        recursive: Whether to search subdirectories
        
    Returns:
        Result dictionary
    """
    service = WebhookSenderService(webhook_url)
    return service.send_directory(directory, recursive=recursive)


def send_year(year: str, webhook_url: str = None) -> dict:
    """
    Send all PDFs from a specific year folder.
    
    Args:
        year: Year to process (e.g., "2024")
        webhook_url: Optional custom webhook URL
        
    Returns:
        Result dictionary
    """
    service = WebhookSenderService(webhook_url)
    return service.send_year(year)


def send_all_years(webhook_url: str = None) -> dict:
    """
    Send all PDFs from all year folders.
    
    Args:
        webhook_url: Optional custom webhook URL
        
    Returns:
        Result dictionary
    """
    service = WebhookSenderService(webhook_url)
    return service.send_all_years()

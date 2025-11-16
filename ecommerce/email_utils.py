import logging
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# email logger
email_logger = logging.getLogger('email_notifications')
email_logger.setLevel(logging.INFO)

# file handler
log_file = LOGS_DIR / 'email.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# formatter
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add handler to logger
if not email_logger.handlers:
    email_logger.addHandler(file_handler)


def send_order_confirmation(order):

    message = (
        f"Order Confirmation - Order #{order.id}\n"
        f"  Customer: {order.created_by.email}\n"
        f"  Company: {order.company.name}\n"
        f"  Product: {order.product.name}\n"
        f"  Quantity: {order.quantity}\n"
        f"  Status: {order.status}\n"
    )
    email_logger.info(message)

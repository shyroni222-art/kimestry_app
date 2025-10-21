import requests
from typing import Optional
from src.utils.models import EnvModel
from src.utils.constants import MICK_API_BASE_URL
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


def get_database_schema(env_id: str) -> Optional[EnvModel]:
    """
    Retrieve database schema for a specific environment from the Mick API
    """
    logger.info(f"Requesting schema for environment {env_id}")
    
    # Return different schemas based on environment
    if env_id == "env1":
        return {
            "env_id": "env1",
            "schemas": [
                {
                    "schema_id": "schema_001",
                    "schema_name": "User Data",
                    "description": "Schema containing user profile and account information.",
                    "fields": [
                        {
                            "field_id": "field_001",
                            "field_name": "username",
                            "example_values": ["john_doe", "jane_smith", "bob_johnson"],
                            "mapping_history": ["user_name", "user_handle", "full_name"],
                            "value_options": None,
                            "regex": "^[a-zA-Z0-9_]{3,20}$",
                            "probability": "0.98",
                            "description": "The unique username selected by the user."
                        },
                        {
                            "field_id": "field_002",
                            "field_name": "email",
                            "example_values": ["john@example.com", "jane@domain.org", "bob@company.com"],
                            "mapping_history": ["user_email", "contact_email", "email_addr"],
                            "value_options": None,
                            "regex": "^[\\w.%+-]+@[\\w.-]+\\.[a-zA-Z]{2,}$",
                            "probability": "0.99",
                            "description": "User's primary email address."
                        },
                        {
                            "field_id": "field_003",
                            "field_name": "account_status",
                            "example_values": ["active", "suspended", "deleted"],
                            "mapping_history": ["status", "user_state", "user_status"],
                            "value_options": ["active", "inactive", "suspended", "deleted"],
                            "regex": None,
                            "probability": "0.92",
                            "description": "The current status of the user's account."
                        }
                    ]
                },
                {
                    "schema_id": "schema_002",
                    "schema_name": "Transaction Data",
                    "description": "Schema describing user transaction records.",
                    "fields": [
                        {
                            "field_id": "field_004",
                            "field_name": "transaction_id",
                            "example_values": ["txn_12345", "txn_67890", "txn_11111"],
                            "mapping_history": ["trans_id", "tx_id", "transaction_id"],
                            "value_options": None,
                            "regex": "^txn_[0-9]{5,}$",
                            "probability": "0.97",
                            "description": "Unique identifier for each transaction."
                        },
                        {
                            "field_id": "field_005",
                            "field_name": "amount",
                            "example_values": ["49.99", "120.00", "5.75"],
                            "mapping_history": ["transaction_amount", "total_cost", "trans_amount"],
                            "value_options": None,
                            "regex": "^[0-9]+(\\.[0-9]{1,2})?$",
                            "probability": "0.95",
                            "description": "The total amount of the transaction in USD."
                        },
                        {
                            "field_id": "field_006",
                            "field_name": "payment_method",
                            "example_values": ["credit_card", "paypal", "bank_transfer"],
                            "mapping_history": ["payment_type", "method", "payment_type"],
                            "value_options": ["credit_card", "paypal", "bank_transfer", "cash"],
                            "regex": None,
                            "probability": "0.93",
                            "description": "The payment method used by the user."
                        }
                    ]
                }
            ]
        }
    elif env_id == "env2":
        return {
            "env_id": "env2",
            "schemas": [
                {
                    "schema_id": "schema_003",
                    "schema_name": "Product Data",
                    "description": "Schema containing product catalog information.",
                    "fields": [
                        {
                            "field_id": "field_007",
                            "field_name": "product_name",
                            "example_values": ["Laptop", "Mouse", "Keyboard"],
                            "mapping_history": ["item_name", "product_name"],
                            "value_options": None,
                            "regex": None,
                            "probability": "0.99",
                            "description": "Name of the product."
                        },
                        {
                            "field_id": "field_008",
                            "field_name": "price",
                            "example_values": [999.99, 25.50, 75.00],
                            "mapping_history": ["product_price", "item_price"],
                            "value_options": None,
                            "regex": "^[0-9]+(\\.[0-9]{1,2})?$",
                            "probability": "0.98",
                            "description": "Price of the product."
                        },
                        {
                            "field_id": "field_009",
                            "field_name": "sku",
                            "example_values": ["C001", "C002", "C003"],
                            "mapping_history": ["customer_id", "item_code"],
                            "value_options": None,
                            "regex": "^C[0-9]{3}$",
                            "probability": "0.95",
                            "description": "SKU or customer ID for the product."
                        }
                    ]
                },
                {
                    "schema_id": "schema_004",
                    "schema_name": "Inventory Data",
                    "description": "Schema containing inventory and stock information.",
                    "fields": [
                        {
                            "field_id": "field_010",
                            "field_name": "item_code",
                            "example_values": ["ITM_001", "ITM_002", "ITM_003"],
                            "mapping_history": ["item_code", "product_id"],
                            "value_options": None,
                            "regex": "^ITM_[0-9]{3}$",
                            "probability": "0.99",
                            "description": "Unique identifier code for the inventory item."
                        },
                        {
                            "field_id": "field_011",
                            "field_name": "item_name",
                            "example_values": ["Product A", "Product B", "Product C"],
                            "mapping_history": ["product_name", "item_name"],
                            "value_options": None,
                            "regex": None,
                            "probability": "0.97",
                            "description": "Name of the inventory item."
                        },
                        {
                            "field_id": "field_012",
                            "field_name": "stock_quantity",
                            "example_values": [100, 50, 200],
                            "mapping_history": ["stock_qty", "quantity"],
                            "value_options": None,
                            "regex": "^[0-9]+$",
                            "probability": "0.96",
                            "description": "Current quantity in stock."
                        },
                        {
                            "field_id": "field_013",
                            "field_name": "reorder_level",
                            "example_values": [20, 10, 50],
                            "mapping_history": ["reorder_level", "min_stock"],
                            "value_options": None,
                            "regex": "^[0-9]+$",
                            "probability": "0.94",
                            "description": "Minimum stock level before reordering."
                        }
                    ]
                }
            ]
        }
    else:
        # Default/unknown environment
        return {
            "env_id": env_id,
            "schemas": []
        }
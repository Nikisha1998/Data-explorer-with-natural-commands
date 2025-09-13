"""
Configuration settings for Data Explorer with Natural Commands
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_PATH = PROJECT_ROOT / "data"
EXPORTS_PATH = PROJECT_ROOT / "exports" 

# Model settings
MODEL_CONFIG = {
    "name": "google/flan-t5-base",
    "max_tokens": 256,
    "temperature": 0.1,
    "fallback_to_rules": True
}

# Available columns in your dataset
DATASET_COLUMNS = [
    'date', 'year', 'quarter', 'month', 'region', 'segment', 'channel',
    'product_category', 'product_name', 'sku', 'units_sold', 'unit_price',
    'discount_pct', 'gross_revenue', 'cogs', 'tax_pct', 'tax_amount',
    'returned_units', 'net_revenue'
]

# Operation types
OPERATIONS = {
    "group_and_aggregate": "Group data and calculate aggregations",
    "filter_data": "Filter data by column values",
    "sort_data": "Sort data by columns", 
    "pivot_data": "Create pivot tables",
    "preview": "Show data overview"
}

# UI settings
UI_CONFIG = {
    "max_suggestions": 3,
    "default_preview_rows": 100,
    "chart_height": 400,
    "export_formats": ["csv", "json", "xlsx"]
}

# Create directories if they don't exist
DATA_PATH.mkdir(exist_ok=True)
EXPORTS_PATH.mkdir(exist_ok=True)

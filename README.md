# Data-explorer-with-natural-commands

A Streamlit-based application enabling non-technical users to query and analyze datasets using natural language. Built for Finkraft.ai's AI Engineer Showcase Round (Team T27).

# Overview

Data Explorer with Natural Commands allows users to upload CSV datasets and query them with plain language (e.g., "show seasonality by region", "top 5 products this quarter"). It combines rule-based and LLM-based query parsing, provides dynamic visualizations (bar, line, heatmap), offers query suggestions for ambiguous inputs, and supports data export (CSV, JSON, XLSX) and session persistence.



# Features

Natural Language Queries: Supports queries like seasonality, top products, and performance analysis.

Dynamic Visualizations: Plotly-based bar, line, and heatmap charts.

Query Suggestions: Provides 2–3 alternative interpretations for vague queries.

Operation Explanations: Human-readable summaries of executed operations.

Data Export: Download results in CSV, JSON, or XLSX formats.

Session Persistence: Save/load query history via JSON.

Efficient Processing: Handles datasets with thousands of rows (tested with 6,199 rows).


# Dataset

File: data/Project5.csv (6,199 rows, 0.8MB)

Columns: date, year, quarter, month, region, segment, channel, product_category, product_name, sku, units_sold, unit_price, discount_pct, gross_revenue, cogs, tax_pct, tax_amount, returned_units, net_revenue

Description: Daily orders with financial metrics across regions, segments, and product categories.



# Setup

### Clone the Repository
```bash
git clone https://github.com/Nikisha1998/Data-explorer-with-natural-commands.git```
cd Data-explorer-with-natural-commands


Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate


`Install dependencies:`

pip install -r requirements.txt


`Run the app:`

streamlit run App.py


# Usage

Upload a CSV file (e.g., data/Project5.csv) via the sidebar.

Enter a natural language query (e.g., "show seasonality by region", "top 5 products this quarter").

View results: data table, visualization (bar, line, or heatmap), operation explanation, and suggestions.

Select alternative suggestions for ambiguous queries.

Export results in CSV, JSON, or XLSX formats.

Save/load session state to persist query history.


# Project Structure

App.py: Main Streamlit application

nlp_manager.py: Query processing and operation execution

nlp_module/core/parser.py: Rule-based and LLM-based query parsing

nlp_module/formatters/ui_formatter.py: Formats suggestions for UI

config.py: Configuration settings

prompt.py: LLM prompt template

data/: Stores datasets (e.g., Project5.csv)

exports/: Stores exported data and session state

requirements.txt: Project dependencies

# Dependencies

Streamlit

Pandas

Plotly

Transformers

Torch

Openpyxl


# Notes

Rule-based parsing is primary; LLM (google/flan-t5-base) serves as a fallback.

Supports operations: filter, sort, group & aggregate, pivot, preview.

Optimized for datasets with columns like date, year, quarter, region, product_name, net_revenue.

# Team

Tanmay Mishra

Nikisha Bongale

Pavan Singh

# # Team

- **Tanmay Mishra**  
- **Nikisha Bongale**  
- **Pavan Singh**  

# Task Division

To ensure smooth collaboration, our team divided responsibilities as follows:

### 1. Data Handling & Operations – *Tanmay Mishra*  
- Implemented CSV uploader & dataset preview  
- Built the core data operations library (filter, sort, group, aggregate, pivot)  
- Optimized handling of mid-sized datasets (thousands of rows)  
- Designed JSON persistence for saving/loading session history  

### 2. Natural Language Processing (NLP) & Suggestions – *Nikisha Bongale*  
- Developed query parsing from plain English to structured operations  
- Handled vague queries by generating 2–3 meaningful suggestions  
- Connected parsed intent to backend operations  
- Generated short, human-readable explanations of results  

### 3. Streamlit UI & User Experience – *Pavan Singh*  
- Designed Streamlit layout (command box, suggestions panel, chart area, explanation panel, export options)  
- Integrated visualizations (Plotly) for bar, line, and heatmap charts  
- Ensured smooth, intuitive user interactions  
- Connected UI actions with the NLP and operations backend  



# Demo

A demo video (demo/demo.mp4) is included in the repository or available at <https://drive.google.com/file/d/166U9IX5g2uTiQFyKMZu8VkT4KAmU-vkQ/view?usp=sharing>.

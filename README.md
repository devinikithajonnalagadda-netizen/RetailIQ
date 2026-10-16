# RetailIQ - Retail Sales & Profit Analytics System

A web app built with Python, MySQL and Streamlit to record products and sales, track revenue and profit, and get simple business insights.

## Features
- Dashboard with revenue, profit, units sold and profit margin
- Add and manage sales records
- Product management
- Rule-based business insights

## Setup
1. Run schema.sql in MySQL Workbench
2. python -m venv .venv
3. .\.venv\Scripts\Activate.ps1
4. python -m pip install -r requirements.txt
5. Set the MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD and MYSQL_DATABASE environment variables
6. python -m streamlit run app.py

## Tech Stack
Python, MySQL, SQL, Streamlit, Pandas
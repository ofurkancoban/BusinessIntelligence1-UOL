"""
Dashboard Setup Script
======================

Automatically creates all 30 KPI cards and dashboard layout.
This script should be run AFTER ETL completes.

Usage:
    python scripts/setup_dashboard.py
"""

import requests
import subprocess
import random
import string
import time

METABASE_URL = "http://localhost:3000"
MB_ADMIN_EMAIL = "admin@admin.com"
MB_ADMIN_PASSWORD = "Password123!"

def get_entity_id():
    """Generate random entity ID for Metabase"""
    return ''.join(random.choices(string.ascii_letters + string.digits + "-_", k=21))

def run_psql(db, query):
    """Execute PostgreSQL query"""
    cmd = ["docker", "exec", "bi_postgres", "psql", "-U", "postgres", "-d", db, "-t", "-c", query]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

def login():
    """Login to Metabase and get session token"""
    payload = {"username": MB_ADMIN_EMAIL, "password": MB_ADMIN_PASSWORD}
    r = requests.post(f"{METABASE_URL}/api/session", json=payload)
    if r.status_code == 200:
        return r.json()['id']
    else:
        raise Exception(f"Login failed: {r.text}")

def get_database_id(session_id):
    """Get database ID for transaction_analytics"""
    headers = {"X-Metabase-Session": session_id}
    r = requests.get(f"{METABASE_URL}/api/database", headers=headers)
    for db in r.json()['data']:
        if db['name'] == 'transaction_analytics':
            return db['id']
    raise Exception("Database 'transaction_analytics' not found")

def create_card(session_id, db_id, name, sql, display="table"):
    """Create a Metabase card"""
    headers = {"X-Metabase-Session": session_id, "Content-Type": "application/json"}
    
    card_data = {
        "name": name,
        "dataset_query": {
            "type": "native",
            "native": {"query": sql},
            "database": db_id
        },
        "display": display,
        "visualization_settings": {}
    }
    
    r = requests.post(f"{METABASE_URL}/api/card", json=card_data, headers=headers)
    if r.status_code == 200:
        return r.json()['id']
    else:
        raise Exception(f"Failed to create card '{name}': {r.text[:200]}")

def create_dashboard(session_id, name):
    """Create a Metabase dashboard"""
    headers = {"X-Metabase-Session": session_id, "Content-Type": "application/json"}
    
    dash_data = {"name": name, "description": "Business Intelligence KPI Dashboard"}
    
    r = requests.post(f"{METABASE_URL}/api/dashboard", json=dash_data, headers=headers)
    if r.status_code == 200:
        return r.json()['id']
    else:
        raise Exception(f"Failed to create dashboard: {r.text[:200]}")

def add_card_to_dashboard(dash_id, card_id, row, col, size_x, size_y):
    """Add card to dashboard using direct SQL"""
    eid = get_entity_id()
    query = f"""
        INSERT INTO report_dashboardcard 
        (created_at, updated_at, size_x, size_y, row, col, card_id, dashboard_id, parameter_mappings, visualization_settings, entity_id)
        VALUES (now(), now(), {size_x}, {size_y}, {row}, {col}, {card_id}, {dash_id}, '[]', '{{}}', '{eid}');
    """
    run_psql("metabase_app_db", query)

print("=" * 70)
print("DASHBOARD SETUP - Creating 30 KPI Cards")
print("=" * 70)
print()

# Wait for Metabase to be ready
print("Waiting for Metabase to be ready...")
max_attempts = 30
for attempt in range(max_attempts):
    try:
        session_id = login()
        print("✓ Metabase is ready")
        break
    except:
        if attempt < max_attempts - 1:
            print(f"  Waiting... ({attempt + 1}/{max_attempts})")
            time.sleep(5)
        else:
            raise Exception("Metabase failed to start")

print()

# Get database ID
db_id = get_database_id(session_id)
print(f"✓ Database ID: {db_id}")
print()

# Sync Schema & Rescan Values
print("Triggering schema sync...")
headers = {"X-Metabase-Session": session_id}
r = requests.post(f"{METABASE_URL}/api/database/{db_id}/sync_schema", headers=headers)
if r.status_code == 200:
    print("✓ Schema sync triggered")
else:
    print(f"⚠ Schema sync failed: {r.status_code}")

print("Triggering field values rescan...")
r = requests.post(f"{METABASE_URL}/api/database/{db_id}/rescan_values", headers=headers)
if r.status_code == 200:
    print("✓ Field values rescan triggered")
else:
    print(f"⚠ Rescan values failed: {r.status_code}")

# Give it a moment to sync
time.sleep(5)
print()

# Create dashboard
print("Creating dashboard...")
dash_id = create_dashboard(session_id, "Financial Transactions Analytics")
print(f"✓ Dashboard created (ID: {dash_id})")
print()

# Define all cards with their SQL queries
print("Creating cards...")
cards = []

# TASK 1: Transaction counts (3 cards)
cards.append(("TASK: Transaction count by year/month/week? | Transactions by Year",
    "SELECT DATE_TRUNC('year', timestamp) as year, COUNT(*) as count FROM fact_transactions GROUP BY year ORDER BY year", "line"))
cards.append(("TASK: Transaction count by year/month/week? | Transactions by Month",
    "SELECT DATE_TRUNC('month', timestamp) as month, COUNT(*) as count FROM fact_transactions GROUP BY month ORDER BY month", "line"))
cards.append(("TASK: Transaction count by year/month/week? | Transactions by Week",
    "SELECT DATE_TRUNC('week', timestamp) as week, COUNT(*) as count FROM fact_transactions GROUP BY week ORDER BY week", "line"))

# TASK 2: Highest revenue MCC (2 cards)
cards.append(("TASK: Which MCC generates highest revenue? | Top 10 MCCs by Revenue",
    "SELECT m.mcc_description, ROUND(SUM(f.amount), 2) as revenue FROM fact_transactions f JOIN dim_merchant m ON f.merchant_id = m.merchant_id GROUP BY m.mcc_description ORDER BY revenue DESC LIMIT 10", "table"))
cards.append(("TASK: Which MCC generates highest revenue? | Revenue Distribution",
    "SELECT m.mcc_description, ROUND(SUM(f.amount), 2) as revenue FROM fact_transactions f JOIN dim_merchant m ON f.merchant_id = m.merchant_id GROUP BY m.mcc_description ORDER BY revenue DESC LIMIT 10", "bar"))

# TASK 3: Utilities (2 cards)
cards.append(("TASK: Avg transaction for Utilities (MCC 4900)? | Utilities Statistics",
    "SELECT COUNT(*) as tx_count, ROUND(AVG(f.amount), 2) as avg_amount, ROUND(SUM(f.amount), 2) as total FROM fact_transactions f JOIN dim_merchant m ON f.merchant_id = m.merchant_id WHERE m.mcc = 4900", "table"))
cards.append(("TASK: Avg transaction for Utilities (MCC 4900)? | Utilities Distribution",
    "SELECT CAST(ROUND(f.amount, 0) AS VARCHAR) as amount_bucket, COUNT(*) as frequency FROM fact_transactions f JOIN dim_merchant m ON f.merchant_id = m.merchant_id WHERE m.mcc = 4900 GROUP BY ROUND(f.amount, 0) ORDER BY ROUND(f.amount, 0)", "bar"))

# TASK 4-5: Income (3 cards)
cards.append(("TASK: Avg yearly income for all clients? | Avg Income (All Clients)",
    "SELECT ROUND(AVG(yearly_income), 2) as avg_income FROM dim_client", "scalar"))
cards.append(("TASK: Avg income for clients with >2 cards? | Avg Income (3+ Cards)",
    "SELECT ROUND(AVG(yearly_income), 2) as avg_income FROM dim_client WHERE num_credit_cards > 2", "scalar"))
cards.append(("TASK: Income by card count? | Income by Card Count",
    "SELECT CAST(num_credit_cards AS VARCHAR) as cards, COUNT(*) as clients, ROUND(AVG(yearly_income), 2) as avg_income FROM dim_client GROUP BY num_credit_cards ORDER BY num_credit_cards", "bar"))

# KPI 1: Debt (2 cards)
cards.append(("KPI: Top 10 clients by debt + avg credit score? | Top 10 Debt Holders",
    "SELECT client_id, total_debt, credit_score FROM dim_client ORDER BY total_debt DESC LIMIT 10", "table"))
cards.append(("KPI: Top 10 clients by debt + avg credit score? | Avg Credit Score",
    "SELECT ROUND(AVG(credit_score), 2) as avg_score FROM (SELECT credit_score FROM dim_client ORDER BY total_debt DESC LIMIT 10) t", "scalar"))

# KPI 2: Dark web (2 cards)
cards.append(("KPI: Credit limit by dark web status? | Credit Limit by Dark Web",
    "SELECT card_on_dark_web, COUNT(*) as cards, ROUND(AVG(credit_limit), 2) as avg_limit FROM dim_card GROUP BY card_on_dark_web", "table"))
cards.append(("KPI: Credit limit by dark web status? | Credit Limit Comparison",
    "SELECT card_on_dark_web, ROUND(AVG(credit_limit), 2) as avg_limit FROM dim_card GROUP BY card_on_dark_web", "bar"))

# KPI 3: Gender (2 cards)
cards.append(("KPI: Per capita income by gender? | Per Capita Income by Gender",
    "SELECT gender, ROUND(AVG(per_capita_income), 2) as avg_income FROM dim_client GROUP BY gender", "table"))
cards.append(("KPI: Per capita income by gender? | Gender Income Comparison",
    "SELECT gender, ROUND(AVG(per_capita_income), 2) as avg_income FROM dim_client GROUP BY gender", "bar"))

# KPI 4: Retirement (2 cards)
cards.append(("KPI: Avg debt for clients within 10y of retirement? | Retirement Debt",
    "SELECT ROUND(AVG(total_debt), 2) as avg_debt FROM dim_client WHERE (retirement_age - current_age) <= 10 AND (retirement_age - current_age) >= 0", "scalar"))
cards.append(("KPI: Avg debt for clients within 10y of retirement? | Retirement Stats",
    "SELECT COUNT(*) as clients, ROUND(AVG(total_debt), 2) as avg_debt, ROUND(AVG(current_age), 1) as avg_age, ROUND(AVG(retirement_age), 1) as avg_ret_age FROM dim_client WHERE (retirement_age - current_age) <= 10 AND (retirement_age - current_age) >= 0", "table"))

# KPI 5: Refunds (2 cards)
cards.append(("KPI: Refund % for Dept Stores (MCC 5311)? | Dept Stores Refund %",
    "SELECT ROUND(100.0 * SUM(CASE WHEN f.amount < 0 THEN 1 ELSE 0 END) / COUNT(*), 4) as refund_pct FROM fact_transactions f JOIN dim_merchant m ON f.merchant_id = m.merchant_id WHERE m.mcc = 5311", "scalar"))
cards.append(("KPI: Refund % for Dept Stores (MCC 5311)? | Dept Stores Analysis",
    "SELECT COUNT(*) as total_tx, SUM(CASE WHEN f.amount < 0 THEN 1 ELSE 0 END) as refunds, ROUND(100.0 * SUM(CASE WHEN f.amount < 0 THEN 1 ELSE 0 END) / COUNT(*), 4) as pct, ROUND(SUM(CASE WHEN f.amount < 0 THEN f.amount ELSE 0 END), 2) as refund_amt, ROUND(SUM(CASE WHEN f.amount >= 0 THEN f.amount ELSE 0 END), 2) as sales_amt FROM fact_transactions f JOIN dim_merchant m ON f.merchant_id = m.merchant_id WHERE m.mcc = 5311", "table"))

# KPI 6: Custom risk (2 cards)
cards.append(("KPI: Custom - High-value tx risk by credit tier? | Risk Analysis",
    "SELECT CASE WHEN c.credit_score >= 750 THEN 'Excellent (750+)' WHEN c.credit_score >= 700 THEN 'Good (700-749)' WHEN c.credit_score >= 650 THEN 'Fair (650-699)' ELSE 'Poor (<650)' END as tier, COUNT(*) as high_value_tx FROM fact_transactions f JOIN dim_client c ON f.client_id = c.client_id WHERE f.amount > 500 GROUP BY tier ORDER BY tier", "table"))
cards.append(("KPI: Custom - High-value tx risk by credit tier? | Risk Distribution",
    "SELECT CASE WHEN c.credit_score >= 750 THEN 'Excellent (750+)' WHEN c.credit_score >= 700 THEN 'Good (700-749)' WHEN c.credit_score >= 650 THEN 'Fair (650-699)' ELSE 'Poor (<650)' END as tier, COUNT(*) as count FROM fact_transactions f JOIN dim_client c ON f.client_id = c.client_id WHERE f.amount > 500 GROUP BY tier ORDER BY tier", "bar"))

# KPI 7-8: Core metrics (5 cards)
cards.append(("KPI: Total transaction volume? | Total Transaction Volume",
    "SELECT ROUND(SUM(amount), 2) as total_volume FROM fact_transactions", "scalar"))
cards.append(("KPI: Average credit score? | Average Credit Score",
    "SELECT ROUND(AVG(credit_score), 2) as avg_score FROM dim_client", "scalar"))
cards.append(("KPI: Card brand distribution? | Card Brand Distribution",
    "SELECT card_brand, COUNT(*) as count, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as pct FROM dim_card GROUP BY card_brand ORDER BY count DESC", "table"))
cards.append(("KPI: Card brand distribution? | Card Brand Share",
    "SELECT card_brand, COUNT(*) as count FROM dim_card GROUP BY card_brand ORDER BY count DESC", "bar"))
cards.append(("KPI: Avg transaction (excl. refunds)? | Avg Transaction Amount",
    "SELECT ROUND(AVG(amount), 2) as avg_amount FROM fact_transactions WHERE amount > 0", "scalar"))

# KPI 9: CLV (3 cards)
cards.append(("KPI: Custom - Customer Lifetime Value | Top 10 CLV Customers",
    "SELECT c.client_id, COUNT(f.transaction_id) as tx_count, ROUND(SUM(f.amount), 2) as total_spent, ROUND((SUM(f.amount) * 0.4) + (COUNT(f.transaction_id) * 10) + (EXTRACT(DAYS FROM (MAX(f.timestamp) - MIN(f.timestamp))) * 0.1), 2) as clv_score FROM dim_client c JOIN fact_transactions f ON c.client_id = f.client_id GROUP BY c.client_id ORDER BY clv_score DESC LIMIT 10", "table"))
cards.append(("KPI: Custom - Customer Lifetime Value | CLV Distribution",
    "SELECT CASE WHEN clv >= 1000000 THEN 'Platinum (1M+)' WHEN clv >= 500000 THEN 'Gold (500K-1M)' WHEN clv >= 100000 THEN 'Silver (100K-500K)' ELSE 'Bronze (<100K)' END as tier, COUNT(*) as customers FROM (SELECT (SUM(f.amount) * 0.4) + (COUNT(f.transaction_id) * 10) + (EXTRACT(DAYS FROM (MAX(f.timestamp) - MIN(f.timestamp))) * 0.1) as clv FROM dim_client c JOIN fact_transactions f ON c.client_id = f.client_id GROUP BY c.client_id) t GROUP BY tier ORDER BY tier", "bar"))
cards.append(("KPI: Business metrics summary | Business Metrics Summary",
    "SELECT (SELECT ROUND(SUM(amount), 2)::text FROM fact_transactions) as \"Total Volume\", (SELECT ROUND(AVG(credit_score), 2)::text FROM dim_client) as \"Avg Credit Score\", (SELECT COUNT(*)::text FROM fact_transactions) as \"Total Transactions\", (SELECT COUNT(*)::text FROM dim_client) as \"Total Clients\"", "table"))

# Create all cards
card_ids = []
for idx, (name, sql, display) in enumerate(cards, 1):
    card_id = create_card(session_id, db_id, name, sql, display)
    card_ids.append(card_id)
    print(f"  ✓ Created card {idx}/30: {name[:50]}...")

print()
print(f"✓ Created {len(card_ids)} cards")
print()

# Add cards to dashboard with layout
print("Adding cards to dashboard...")

layout = [
    # TASK section - Transactions (3 cards)
    (card_ids[0], 0, 0, 8, 6),
    (card_ids[1], 0, 8, 8, 6),
    (card_ids[2], 0, 16, 8, 6),
    
    # Revenue MCC (2 cards)
    (card_ids[3], 6, 0, 12, 8),
    (card_ids[4], 6, 12, 12, 8),
    
    # Utilities (2 cards)
    (card_ids[5], 14, 0, 12, 6),
    (card_ids[6], 14, 12, 12, 6),
    
    # Income (3 cards)
    (card_ids[7], 20, 0, 8, 4),
    (card_ids[8], 20, 8, 8, 4),
    (card_ids[9], 20, 16, 8, 6),
    
    # KPI section - Debt (2 cards)
    (card_ids[10], 26, 0, 16, 8),
    (card_ids[11], 26, 16, 8, 6),
    
    # Dark web (2 cards)
    (card_ids[12], 34, 0, 12, 6),
    (card_ids[13], 34, 12, 12, 6),
    
    # Gender (2 cards)
    (card_ids[14], 40, 0, 12, 6),
    (card_ids[15], 40, 12, 12, 6),
    
    # Retirement (2 cards)
    (card_ids[16], 46, 0, 8, 4),
    (card_ids[17], 46, 8, 16, 3),
    
    # Refunds (2 cards)
    (card_ids[18], 50, 0, 8, 4),
    (card_ids[19], 50, 8, 16, 3),
    
    # Custom risk (2 cards)
    (card_ids[20], 54, 0, 12, 8),
    (card_ids[21], 54, 12, 12, 10),
    
    # Core metrics (5 cards)
    (card_ids[22], 64, 0, 8, 4),
    (card_ids[23], 64, 8, 8, 4),
    (card_ids[24], 68, 0, 12, 6),
    (card_ids[25], 68, 12, 12, 6),
    (card_ids[26], 64, 16, 8, 4),
    
    # CLV (3 cards)
    (card_ids[27], 74, 0, 12, 8),
    (card_ids[28], 74, 12, 12, 8),
    (card_ids[29], 82, 0, 24, 4),
]

for card_id, row, col, sx, sy in layout:
    add_card_to_dashboard(dash_id, card_id, row, col, sx, sy)

print(f"✓ Added {len(layout)} cards to dashboard")
print()

print("=" * 70)
print("DASHBOARD SETUP COMPLETE!")
print("=" * 70)
print(f"Dashboard ID: {dash_id}")
print(f"Total Cards: {len(card_ids)}")
print(f"Dashboard URL: {METABASE_URL}/dashboard/{dash_id}")
print("=" * 70)

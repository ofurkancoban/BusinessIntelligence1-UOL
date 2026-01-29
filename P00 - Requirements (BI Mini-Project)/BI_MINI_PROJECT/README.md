# Business Intelligence Mini-Project

### Ömer Furkan Çoban

An end-to-end BI solution for analyzing credit card transactions, detecting fraud, and visualizing key performance indicators (KPIs) using PostgreSQL and Metabase.

## 🏗️ Architecture

The project uses a containerized architecture with three main services:

1. **PostgreSQL (`bi_postgres`)**: Stores the Star Schema data warehouse (Fact + Dimensions).
2. **Metabase (`bi_metabase`)**: Provides the visualization layer and dashboard.
3. **Data Importer (`bi_data_importer`)**: Python container for running ETL scripts.

### Star Schema

- **Fact Table**: `fact_transactions` (13.3M+ records)
- **Dimension Tables**:
  - `dim_client`: Customer demographics and financial data.
  - `dim_card`: Credit/debit card details.
  - `dim_merchant`: Merchant location and category (MCC) info.

![Star Schema Diagram](https://mermaid.ink/img/ZXJEaWFncmFtCiAgICBkaW1fY2xpZW50IHx8LS1veyBmYWN0X3RyYW5zYWN0aW9ucyA6ICJpbml0aWF0ZXMiCiAgICBkaW1fY2FyZCB8fC0tb3sgZmFjdF90cmFuc2FjdGlvbnMgOiAidXNlZCBmb3IiCiAgICBkaW1fbWVyY2hhbnQgfHwtLW97IGZhY3RfdHJhbnNhY3Rpb25zIDogInByb2Nlc3NlcyIKICAgIGRpbV9jbGllbnQgfHwtLW97IGRpbV9jYXJkIDogIm93bnMiCgogICAgZmFjdF90cmFuc2FjdGlvbnMgewogICAgICAgIEJJR0lOVCB0cmFuc2FjdGlvbl9pZCBQSwogICAgICAgIEJJR0lOVCBjbGllbnRfaWQgRksKICAgICAgICBCSUdJTlQgY2FyZF9pZCBGSwogICAgICAgIEJJR0lOVCBtZXJjaGFudF9pZCBGSwogICAgICAgIERFQ0lNQUwgYW1vdW50CiAgICAgICAgVElNRVNUQU1QIHRpbWVzdGFtcAogICAgICAgIEJPT0xFQU4gaXNfZnJhdWQKICAgIH0KCiAgICBkaW1fY2xpZW50IHsKICAgICAgICBCSUdJTlQgY2xpZW50X2lkIFBLCiAgICAgICAgREVDSU1BTCB5ZWFybHlfaW5jb21lCiAgICAgICAgSU5URUdFUiBjcmVkaXRfc2NvcmUKICAgICAgICBJTlRFR0VSIGN1cnJlbnRfYWdlCiAgICAgICAgVkFSQ0hBUiBnZW5kZXIKICAgIH0KCiAgICBkaW1fY2FyZCB7CiAgICAgICAgQklHSU5UIGNhcmRfaWQgUEsKICAgICAgICBCSUdJTlQgY2xpZW50X2lkIEZLCiAgICAgICAgVkFSQ0hBUiBjYXJkX2JyYW5kCiAgICAgICAgVkFSQ0hBUiBjYXJkX3R5cGUKICAgICAgICBERUNJTUFMIGNyZWRpdF9saW1pdAogICAgfQoKICAgIGRpbV9tZXJjaGFudCB7CiAgICAgICAgQklHSU5UIG1lcmNoYW50X2lkIFBLCiAgICAgICAgSU5URUdFUiBtY2MKICAgICAgICBWQVJDSEFSIG1lcmNoYW50X2NpdHkKICAgICAgICBWQVJDSEFSIG1lcmNoYW50X3N0YXRlCiAgICB9)

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running.
- Data files placed in the `data/` directory:
  - `transactions.csv`
  - `users.csv`
  - `cards.csv`
  - `mcc_codes.csv`
  - `train_labels.json`

### Deployment

1. **Run the deployment script**:

   First, ensure the script is executable:

   ```bash
   chmod +x deploy.sh
   ```

   Then execute it:

   ```bash
   ./deploy.sh
   ```

   This script will:

   - Check for required files and tools.
   - Start Docker containers.
   - Wait for services to be ready.
   - Run the ETL pipeline (populating the database).
   - Configure Metabase and create the "KPI Dashboard - Data Verification" automatically.
2. **Access the Dashboard**:

   - **URL**: [http://localhost:3000](http://localhost:3000)
   - **Email**: `admin@admin.com`
   - **Password**: `Password123!`
   - **Navigation**: Dashboards > Financial Transactions Analytics

## 🛠️ scripts Directory

- `etl_main.py`: Main ETL pipeline (Extracts CSVs, Transforms to Star Schema, Loads to Postgres).
- `setup_dashboard.py`: Configures Metabase via API, creates 30+ Cards, and builds the Dashboard layout.

## 🔄 ETL Pipeline & Data Processing

The `etl_main.py` script performs significant data processing to ensure data quality and analytical readiness:

1. **Cleaning**:

   - **Currency Conversion**: Strips symbols (e.g., `$`, `,`) from fields like `amount`, `yearly_income`, and `total_debt` to convert them to numeric types.
   - **Timestamp Parsing**: Converts string date formats into PostgreSQL-compatible `TIMESTAMP` objects.
2. **Enrichment**:

   - **Fraud Labelling**: Joins transaction data with `train_labels.json` to flag transactions as `is_fraud` (True/False).
   - **MCC Descriptions**: Maps raw Merchant Category Codes (MCC) to human-readable descriptions (e.g., "Airlines", "Hotels") using `mcc_codes.json`.
3. **Normalization (Star Schema)**:

   - Transforms flat CSV data into a relational **Star Schema**.
   - **De-duplication**: Extracts unique Client, Card, and Merchant entities into their respective Dimension tables (`dim_client`, `dim_card`, `dim_merchant`) to eliminate redundancy.

## 📊 Key Metrics Implemented

- **Transaction Volume**: Total volume, counts by period (Year/Month/Week).
- **Fraud Analysis**: Fraud rates by Merchant Category (MCC) and State.
- **Customer Risk**: Debt analysis, specific metrics for customers with >2 cards.
- **Utilities**: Special analysis for MCC 4900 (Utilities) transactions.
- **Business Metrics**: Consolidated view of Total Volume, Avg Credit Score, etc.

## ❓ Troubleshooting

**Metabase shows "Still Waiting..." or generic errors:**

- Ensure the ETL completed successfully.
- Run `docker logs bi_metabase` to check for specific internal errors.

**Visualizations look wrong:**

- Ensure `setup_dashboard.py` ran *after* the ETL.
- You can re-run the dashboard setup manually:

  ```bash
  docker exec bi_data_importer python /scripts/setup_dashboard.py
  ```

**Database connection failed:**

- Check container status: `docker ps`
- Ensure port 5432 is not occupied by a local Postgres instance.

"""
ETL Pipeline for Fraud Detection Star Schema
==============================================

This script performs Extract, Transform, Load operations to populate
the fraud detection data warehouse with a star schema design.

Author: BI Mini Project
Date: 2026-01-30
Version: 3.0

ETL Phases:
1. EXTRACT: Read CSV and JSON source files
2. TRANSFORM: Clean, enrich, and prepare data
3. LOAD: Insert into PostgreSQL star schema

Star Schema:
- Fact: fact_transactions (13.3M records)
- Dimensions: dim_client, dim_card, dim_merchant
"""

import pandas as pd
import numpy as np
import json
import psycopg2
from psycopg2.extras import execute_batch
import os
import sys
from datetime import datetime
import time

# ============================================
# CONFIGURATION
# ============================================

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'transaction_analytics'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

DATA_DIR = '/data'
BATCH_SIZE = 100000  # Increased for faster processing

# ============================================
# UTILITY FUNCTIONS
# ============================================

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)

def get_db_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(**DB_CONFIG)

def clean_currency(value):
    """Remove $ symbol and convert to float"""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        return float(value.replace('$', '').replace(',', ''))
    return float(value)

def parse_timestamp(value):
    """Parse timestamp string to datetime"""
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value)
    except:
        return None

# ============================================
# PHASE 1: EXTRACT
# ============================================

def extract_data():
    """
    Extract data from source files
    
    Returns:
        dict: Dictionary containing all source dataframes
    """
    log("=" * 60)
    log("PHASE 1: EXTRACT - Reading source files")
    log("=" * 60)
    
    data = {}
    
    # 1. Load Users Data
    log("Loading users_data.csv...")
    users_file = f"{DATA_DIR}/users_data.csv"
    data['users'] = pd.read_csv(users_file)
    log(f"  ✓ Loaded {len(data['users']):,} users")
    
    # 2. Load Cards Data
    log("Loading cards_data.csv...")
    cards_file = f"{DATA_DIR}/cards_data.csv"
    data['cards'] = pd.read_csv(cards_file)
    log(f"  ✓ Loaded {len(data['cards']):,} cards")
    
    # 3. Load MCC Codes
    log("Loading mcc_codes.json...")
    mcc_file = f"{DATA_DIR}/mcc_codes.json"
    with open(mcc_file, 'r') as f:
        data['mcc'] = json.load(f)
    log(f"  ✓ Loaded {len(data['mcc'])} MCC codes")
    
    # 4. Load Fraud Labels
    log("Loading train_fraud_labels.json...")
    fraud_file = f"{DATA_DIR}/train_fraud_labels.json"
    with open(fraud_file, 'r') as f:
        data['fraud_labels'] = json.load(f)
    log(f"  ✓ Loaded {len(data['fraud_labels']):,} fraud labels")
    
    # 5. Load Transactions (in chunks for memory efficiency)
    log("Loading transactions_data.csv (chunked)...")
    trans_file = f"{DATA_DIR}/transactions_data.csv"
    data['transactions_file'] = trans_file
    
    # Get total count
    total_lines = sum(1 for _ in open(trans_file)) - 1  # Exclude header
    log(f"  ✓ Found {total_lines:,} transactions")
    
    log("✓ EXTRACT phase complete\n")
    return data

# ============================================
# PHASE 2: TRANSFORM
# ============================================

def transform_clients(users_df):
    """
    Transform users data to dim_client format
    
    Args:
        users_df: Raw users dataframe
        
    Returns:
        DataFrame: Cleaned client dimension data
    """
    log("Transforming dim_client...")
    
    df = users_df.copy()
    
    # Rename columns to match schema
    df = df.rename(columns={'id': 'client_id'})
    
    # Clean currency fields
    for col in ['per_capita_income', 'yearly_income', 'total_debt']:
        df[col] = df[col].apply(clean_currency)
    
    # Ensure correct data types
    df['client_id'] = df['client_id'].astype('int64')
    df['current_age'] = df['current_age'].astype('int32')
    df['retirement_age'] = df['retirement_age'].astype('int32')
    df['birth_year'] = df['birth_year'].astype('int32')
    df['birth_month'] = df['birth_month'].astype('int32')
    df['credit_score'] = df['credit_score'].astype('int32')
    df['num_credit_cards'] = df['num_credit_cards'].astype('int32')
    
    log(f"  ✓ Transformed {len(df):,} clients")
    return df

def transform_cards(cards_df):
    """
    Transform cards data to dim_card format
    
    Args:
        cards_df: Raw cards dataframe
        
    Returns:
        DataFrame: Cleaned card dimension data
    """
    log("Transforming dim_card...")
    
    df = cards_df.copy()
    
    # Rename columns
    df = df.rename(columns={'id': 'card_id'})
    
    # Clean credit limit
    df['credit_limit'] = df['credit_limit'].apply(clean_currency)
    
    # Ensure correct data types
    df['card_id'] = df['card_id'].astype('int64')
    df['client_id'] = df['client_id'].astype('int64')
    df['num_cards_issued'] = df['num_cards_issued'].astype('int32')
    df['year_pin_last_changed'] = df['year_pin_last_changed'].astype('int32')
    
    log(f"  ✓ Transformed {len(df):,} cards")
    return df

def transform_merchants(trans_chunk, mcc_dict):
    """
    Extract unique merchants from transactions
    
    Args:
        trans_chunk: Transaction dataframe chunk
        mcc_dict: MCC code to description mapping
        
    Returns:
        DataFrame: Unique merchants with MCC descriptions
    """
    # Extract merchant columns
    merchants = trans_chunk[['merchant_id', 'merchant_city', 'merchant_state', 'zip', 'mcc']].copy()
    
    # Drop duplicates
    merchants = merchants.drop_duplicates(subset=['merchant_id'])
    
    # Add MCC descriptions
    merchants['mcc_description'] = merchants['mcc'].astype(str).map(mcc_dict)
    
    # Ensure correct data types
    merchants['merchant_id'] = merchants['merchant_id'].astype('int64')
    merchants['mcc'] = merchants['mcc'].astype('int32')
    
    return merchants

def transform_transactions(trans_chunk, fraud_labels):
    """
    Transform transaction data to fact table format
    
    Args:
        trans_chunk: Raw transaction dataframe chunk
        fraud_labels: Dictionary of transaction_id -> fraud_label
        
    Returns:
        DataFrame: Cleaned transaction fact data
    """
    df = trans_chunk.copy()
    
    # Rename columns
    df = df.rename(columns={'id': 'transaction_id', 'date': 'timestamp'})
    
    # Clean amount
    df['amount'] = df['amount'].apply(clean_currency)
    
    # Parse timestamp
    df['timestamp'] = df['timestamp'].apply(parse_timestamp)
    
    # Add fraud labels
    df['is_fraud'] = df['transaction_id'].astype(str).map(fraud_labels).fillna(False).astype(bool)
    
    # Select only fact table columns
    fact_cols = ['transaction_id', 'client_id', 'card_id', 'merchant_id', 
                 'amount', 'timestamp', 'use_chip', 'errors', 'is_fraud']
    df = df[fact_cols]
    
    # Ensure correct data types
    df['transaction_id'] = df['transaction_id'].astype('int64')
    df['client_id'] = df['client_id'].astype('int64')
    df['card_id'] = df['card_id'].astype('int64')
    df['merchant_id'] = df['merchant_id'].astype('int64')
    
    return df

# ============================================
# PHASE 3: LOAD
# ============================================

def load_dimension(conn, table_name, df, columns):
    """
    Load dimension table using batch insert
    
    Args:
        conn: Database connection
        table_name: Target table name
        df: DataFrame to load
        columns: List of column names
    """
    log(f"Loading {table_name}...")
    
    cursor = conn.cursor()
    
    # Prepare INSERT statement
    cols_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
    
    # Convert dataframe to list of tuples
    data = [tuple(row) for row in df[columns].values]
    
    # Batch insert
    execute_batch(cursor, insert_sql, data, page_size=BATCH_SIZE)
    conn.commit()
    
    log(f"  ✓ Loaded {len(df):,} records into {table_name}")

def load_fact_chunked(conn, trans_file, fraud_labels, mcc_dict):
    """
    Load fact table in chunks for memory efficiency
    
    Args:
        conn: Database connection
        trans_file: Path to transactions CSV
        fraud_labels: Fraud label dictionary
        mcc_dict: MCC code dictionary
    """
    log("=" * 60)
    log("PHASE 3: LOAD - Inserting into database")
    log("=" * 60)
    
    cursor = conn.cursor()
    
    # Prepare INSERT statement for facts
    fact_cols = ['transaction_id', 'client_id', 'card_id', 'merchant_id', 
                 'amount', 'timestamp', 'use_chip', 'errors', 'is_fraud']
    cols_str = ', '.join(fact_cols)
    placeholders = ', '.join(['%s'] * len(fact_cols))
    fact_insert_sql = f"INSERT INTO fact_transactions ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
    
    # Prepare INSERT for merchants
    merch_cols = ['merchant_id', 'merchant_city', 'merchant_state', 'zip', 'mcc', 'mcc_description']
    merch_cols_str = ', '.join(merch_cols)
    merch_placeholders = ', '.join(['%s'] * len(merch_cols))
    merch_insert_sql = f"INSERT INTO dim_merchant ({merch_cols_str}) VALUES ({merch_placeholders}) ON CONFLICT DO NOTHING"
    
    # Track unique merchants
    loaded_merchants = set()
    total_transactions = 0
    total_merchants = 0
    
    # Process in chunks
    chunk_num = 0
    for chunk in pd.read_csv(trans_file, chunksize=BATCH_SIZE):
        chunk_num += 1
        start_time = time.time()
        
        # Transform merchants from this chunk
        merchants_df = transform_merchants(chunk, mcc_dict)
        
        # Load new merchants
        new_merchants = merchants_df[~merchants_df['merchant_id'].isin(loaded_merchants)]
        if len(new_merchants) > 0:
            merch_data = [tuple(row) for row in new_merchants[merch_cols].values]
            execute_batch(cursor, merch_insert_sql, merch_data, page_size=1000)
            loaded_merchants.update(new_merchants['merchant_id'].values)
            total_merchants += len(new_merchants)
        
        # Transform and load transactions
        facts_df = transform_transactions(chunk, fraud_labels)
        fact_data = [tuple(row) for row in facts_df[fact_cols].values]
        execute_batch(cursor, fact_insert_sql, fact_data, page_size=BATCH_SIZE)
        
        total_transactions += len(facts_df)
        
        # Commit every chunk
        conn.commit()
        
        elapsed = time.time() - start_time
        log(f"  Chunk {chunk_num}: {len(facts_df):,} transactions, "
            f"{len(new_merchants)} new merchants ({elapsed:.1f}s) "
            f"[Total: {total_transactions:,} trans, {total_merchants:,} merchants]")
    
    log(f"✓ Loaded {total_transactions:,} transactions and {total_merchants:,} merchants")

# ============================================
# MAIN ETL PIPELINE
# ============================================

def main():
    """Execute complete ETL pipeline"""
    
    log("=" * 60)
    log("ETL PIPELINE")
    log("=" * 60)
    log(f"Database: {DB_CONFIG['database']}")
    log(f"Data Directory: {DATA_DIR}")
    log(f"Batch Size: {BATCH_SIZE:,}")
    log("")
    
    start_time = time.time()
    
    try:
        # PHASE 1: EXTRACT
        data = extract_data()
        
        # PHASE 2: TRANSFORM
        log("=" * 60)
        log("PHASE 2: TRANSFORM - Cleaning and enriching data")
        log("=" * 60)
        
        clients_df = transform_clients(data['users'])
        cards_df = transform_cards(data['cards'])
        
        log("✓ TRANSFORM phase complete\n")
        
        # PHASE 3: LOAD
        conn = get_db_connection()
        
        # Load dimensions first (order matters due to foreign keys)
        log("Loading dimension tables...")
        
        client_cols = ['client_id', 'current_age', 'retirement_age', 'birth_year', 
                      'birth_month', 'gender', 'address', 'latitude', 'longitude',
                      'per_capita_income', 'yearly_income', 'total_debt', 
                      'credit_score', 'num_credit_cards']
        load_dimension(conn, 'dim_client', clients_df, client_cols)
        
        card_cols = ['card_id', 'client_id', 'card_brand', 'card_type', 'card_number',
                    'expires', 'cvv', 'has_chip', 'num_cards_issued', 'credit_limit',
                    'acct_open_date', 'year_pin_last_changed', 'card_on_dark_web']
        load_dimension(conn, 'dim_card', cards_df, card_cols)
        
        log("")
        
        # Load fact table and remaining merchants
        load_fact_chunked(conn, data['transactions_file'], data['fraud_labels'], data['mcc'])
        
        conn.close()
        
        # Summary
        elapsed = time.time() - start_time
        log("")
        log("=" * 60)
        log("ETL PIPELINE COMPLETE")
        log("=" * 60)
        log(f"Total Time: {elapsed/60:.1f} minutes")
        log(f"Database: {DB_CONFIG['database']}")
        log("")
        log("Next Steps:")
        log("  1. Verify data: docker exec bi_postgres psql -U postgres -d transaction_analytics -c '\\dt'")
        log("  2. Check counts: docker exec bi_postgres psql -U postgres -d transaction_analytics -c 'SELECT COUNT(*) FROM fact_transactions;'")
        log("  3. Access Metabase: http://localhost:3000")
        log("=" * 60)
        
    except Exception as e:
        log(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

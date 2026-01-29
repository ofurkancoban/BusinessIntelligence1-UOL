#!/bin/bash

# ============================================
# DEPLOYMENT SCRIPT
# Business Intelligence Mini-Project
# ============================================

set -e  # Exit on error

echo "============================================"
echo "BI MINI-PROJECT DEPLOYMENT"
echo "============================================"
echo ""

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Error: Docker daemon is not running"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo "❌ Error: curl is not installed (required for downloading data)"
    exit 1
fi

if ! command -v unzip &> /dev/null; then
    echo "❌ Error: unzip is not installed (required for extracting data)"
    exit 1
fi

echo "✓ Docker, curl, and unzip are ready"
echo ""

# Step 2: Check data files
echo "Step 2: Checking data files..."
required_files=("data/transactions.csv" "data/users.csv" "data/cards.csv" "data/mcc_codes.csv" "data/train_labels.json")
missing_files=()

check_files() {
    missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
}

check_files

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "⚠️  Missing required data files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    read -p "Do you want to download and unzip the dataset now? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        DEFAULT_URL="https://cloud.uol.de/public.php/dav/files/DRBP72f7odnrN6k/financial-transactions.zip"
        echo "Default URL: $DEFAULT_URL"
        read -p "Enter direct download URL (zip file) [Press Enter for Default]: " DATA_URL
        
        if [ -z "$DATA_URL" ]; then
            DATA_URL="$DEFAULT_URL"
        fi

        echo "Downloading dataset..."
        mkdir -p data
        if curl -L -o data_archive.zip "$DATA_URL"; then
            echo "Extracting..."
            if unzip -o data_archive.zip -d data/; then
                echo "✓ Download and extraction complete."
                rm data_archive.zip
            else
                echo "❌ Error: Extraction failed."
                exit 1
            fi
        else
            echo "❌ Error: Download failed."
            exit 1
        fi
        
        # Re-check files
        check_files
        if [ ${#missing_files[@]} -ne 0 ]; then
             echo "❌ Error: Some files are still missing after download:"
             for file in "${missing_files[@]}"; do
                 echo "  - $file"
             done
             echo "Please check the zip file structure."
             exit 1
        else
            echo "✓ All data files present now."
        fi
        
    else
        echo "❌ Error: Cannot proceed without data files."
        exit 1
    fi
fi

echo "✓ All data files confirmed"
echo ""

echo "✓ All data files present"
echo ""

# Step 3: Start Docker services
echo "Step 3: Starting Docker services..."
docker-compose down -v 2>/dev/null || true
docker-compose up -d

echo "✓ Services started"
echo ""

# Step 4: Wait for PostgreSQL
echo "Step 4: Waiting for PostgreSQL to be ready..."
sleep 10

max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec bi_postgres pg_isready -U postgres &> /dev/null; then
        echo "✓ PostgreSQL is ready"
        break
    fi
    attempt=$((attempt + 1))
    echo "  Waiting... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Error: PostgreSQL failed to start"
    exit 1
fi

echo ""

# Step 5: Wait for Metabase
echo "Step 5: Waiting for Metabase to be ready..."
sleep 5
echo "✓ Metabase starting (will be ready in ~30 seconds)"
echo ""

# Step 6: Run ETL
echo "Step 6: Running ETL pipeline..."
echo "⏱️  This will take approximately 60 minutes for 13.3M records"
echo ""
read -p "Do you want to start ETL now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Create required views if not already present (handled by init scripts but good to be safe)
    # docker exec bi_postgres psql -U postgres -d transaction_analytics -f /docker-entrypoint-initdb.d/02_create_viz_views.sql 2>/dev/null || true

    docker exec bi_data_importer python /scripts/etl_main.py
    echo ""
    echo "✓ ETL completed successfully"
    echo ""
    
    # Step 7: Setup Dashboard
    echo "Step 7: Setting up Metabase dashboard..."
    echo "Creating 30 KPI cards and dashboard layout..."
    # Install requests if not present in container (it should be)
    docker exec bi_data_importer pip install requests > /dev/null 2>&1 || true
    docker exec bi_data_importer python /scripts/setup_dashboard.py
    echo "✓ Dashboard setup completed"
else
    echo "⚠️  ETL skipped. Run manually with:"
    echo "   docker exec bi_data_importer python /scripts/etl_main.py"
    echo "   docker exec bi_data_importer python /scripts/setup_dashboard.py"
fi

echo ""
echo "============================================"
echo "DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo "📊 Dashboard URL: http://localhost:3000"
echo "📧 Email: admin@admin.com"
echo "🔑 Password: Password123!"
echo ""
echo "Navigate to: Dashboard → 'Financial Transactions Analytics'"
echo ""
echo "============================================"

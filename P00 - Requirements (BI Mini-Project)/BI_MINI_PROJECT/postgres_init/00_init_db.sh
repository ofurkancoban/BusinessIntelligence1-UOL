#!/bin/bash
set -e

# Function to create user and database
create_db_and_user() {
	local database=$1
	echo "  Creating database '$database'..."
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	    SELECT 'CREATE DATABASE $database'
	    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$database')\gexec
EOSQL
}

# Create the databases requested (fraud_detection is default, so just ensure metabase_app_db exists)
# POSTGRES_DB is already created by the image.
# We need to create 'metabase_app_db'
create_db_and_user metabase_app_db

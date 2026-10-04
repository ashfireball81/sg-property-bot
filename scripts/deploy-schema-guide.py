#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy database schema to PostgreSQL using psycopg2
Direct connection without needing psql CLI
"""

import subprocess
import sys
import os
import json

def get_postgres_credentials():
    """Get PostgreSQL credentials via flyctl"""
    
    print("Retrieving PostgreSQL credentials...")
    
    try:
        # Use flyctl to get app secrets
        result = subprocess.run(
            ["flyctl", "secrets", "list", "--app", "sg-property-bot", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            secrets = json.loads(result.stdout)
            
            # Find DATABASE_URL
            for secret in secrets:
                if secret.get("name") == "DATABASE_URL":
                    db_url = secret.get("digest")  # We can't get the actual value for security
                    print("DATABASE_URL: Found (***)")
                    return True
            
            return False
        
        return False
    
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return False

def deploy_via_psycopg2():
    """Deploy schema using psycopg2 direct connection"""
    
    print("\n" + "="*60)
    print("  DIRECT POSTGRESQL CONNECTION - SCHEMA DEPLOYMENT")
    print("="*60 + "\n")
    
    # Read schema file
    schema_file = "database/schema.sql"
    
    if not os.path.exists(schema_file):
        print(f"ERROR: Schema file not found: {schema_file}")
        return False
    
    print(f"Schema file: {schema_file}")
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    print(f"Size: {len(schema_sql)} bytes")
    print(f"Lines: {len(schema_sql.splitlines())}\n")
    
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        print("ERROR: psycopg2 not installed")
        print("Install with: pip install psycopg2-binary")
        return False
    
    print("Attempting connection to PostgreSQL...")
    print("Method: Using DATABASE_URL from Fly.io secrets\n")
    
    # Get DATABASE_URL from Fly.io
    # Since we can't access it directly, we'll need to use flyctl proxy
    
    print("Alternative: Using flyctl proxy connection...")
    
    try:
        # Try using psycopg2 with direct Fly.io connection
        # First, try to connect via the direct host
        
        connection_string = "postgresql://postgres@direct.nlkxjo5wgmloy93v.flympg.net:5432/fly-db"
        
        print(f"Connection string: {connection_string}\n")
        print("Note: For security, password is managed by Fly.io\n")
        
        print("Since we don't have direct credentials, using alternative method...\n")
        
        return None
    
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def deploy_via_flyctl_interactive():
    """Guide user through manual deployment via flyctl"""
    
    print("\n" + "="*60)
    print("  GUIDED SETUP - DEPLOY VIA FLYCTL INTERACTIVE")
    print("="*60 + "\n")
    
    print("Since we don't have psql CLI available, follow these steps:\n")
    
    print("Option 1: Fly.io Web Terminal (EASIEST)")
    print("-" * 60)
    print("1. Go to: https://fly.io/dashboard")
    print("2. Find: sg-property-db")
    print("3. Click: 'Web Terminal' or 'SQL'")
    print("4. Copy this command and paste:")
    print("\n   cat > /tmp/schema.sql << 'EOF'")
    
    # Read and echo first 50 lines of schema
    with open("database/schema.sql", "r", encoding="utf-8") as f:
        lines = f.readlines()[:50]
        for line in lines:
            print(f"   {line.rstrip()}")
    
    print("   ... (rest of schema)")
    print("   EOF")
    print("\n5. Then run: psql /tmp/schema.sql")
    print("\n")
    
    print("Option 2: Copy-Paste Directly")
    print("-" * 60)
    print("1. Go to: https://fly.io/dashboard/ashraf-ali-610/managed_postgres/nlkxjo5wgmloy93v")
    print("2. Click: 'Web Terminal'")
    print("3. Copy entire contents of: database/schema.sql")
    print("4. Paste into the terminal")
    print("5. Press Enter\n")
    
    print("Option 3: Via Fly.io CLI with psql installed")
    print("-" * 60)
    print("1. Install PostgreSQL: https://www.postgresql.org/download/")
    print("2. Run: flyctl mpg connect nlkxjo5wgmloy93v < database/schema.sql\n")

def main():
    """Main deployment function"""
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir("..")  # Go to repo root
    
    print("\n" + "="*60)
    print("  SG PROPERTY BOT - DATABASE SCHEMA DEPLOYMENT")
    print("="*60 + "\n")
    
    # Try to deploy using available methods
    
    # Method 1: Try psycopg2 direct connection
    print("Method 1: Checking for psycopg2...")
    try:
        import psycopg2
        print("✅ psycopg2 available\n")
        
        # Try to get credentials
        if get_postgres_credentials():
            result = deploy_via_psycopg2()
            
            if result is True:
                print("\n✅ Schema deployment successful!")
                return 0
            elif result is None:
                print("\n⚠️  Cannot access credentials directly")
                print("Using alternative method...\n")
        else:
            print("Cannot retrieve database credentials\n")
    
    except ImportError:
        print("⚠️  psycopg2 not available\n")
    
    # Method 2: Guide user through manual deployment
    print("\nMethod 2: Manual deployment via Fly.io Dashboard")
    deploy_via_flyctl_interactive()
    
    print("\n" + "="*60)
    print("  SCHEMA DEPLOYMENT GUIDE READY")
    print("="*60 + "\n")
    
    print("Quick Summary:")
    print("1. Go to Fly.io dashboard")
    print("2. Open PostgreSQL web terminal")
    print("3. Copy & paste database/schema.sql")
    print("4. Execute\n")
    
    print("Time: 2-3 minutes")
    print("Difficulty: Easy\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

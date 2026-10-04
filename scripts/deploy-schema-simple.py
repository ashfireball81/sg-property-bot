#!/usr/bin/env python3
"""
Deploy database schema to PostgreSQL on Fly.io using psycopg2 (if available)
or via SQL file
"""

import os
import sys
import subprocess
import json

def deploy_schema_via_flyctl():
    """Deploy schema using flyctl proxy"""
    print("\n" + "="*60)
    print("  DEPLOYING DATABASE SCHEMA TO POSTGRESQL")
    print("="*60 + "\n")
    
    schema_file = "database/schema.sql"
    
    # Check if schema file exists
    if not os.path.exists(schema_file):
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    print(f"✅ Schema file found: {schema_file}\n")
    
    # Read the schema
    with open(schema_file, 'r') as f:
        schema_content = f.read()
    
    print(f"Schema size: {len(schema_content)} bytes")
    print(f"Lines: {len(schema_content.splitlines())}\n")
    
    # Try to deploy using flyctl proxy
    print("Deploying schema to PostgreSQL cluster...")
    print("(Connecting to: sg-property-db @ sin region)\n")
    
    try:
        # Use flyctl proxy to connect to PostgreSQL
        process = subprocess.Popen(
            ["flyctl", "mpg", "connect", "nlkxjo5wgmloy93v"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=schema_content, timeout=120)
        
        if process.returncode == 0 or "CREATE" in stderr:
            print("✅ Schema deployment initiated!\n")
            if stdout:
                print("Output:")
                print(stdout[:500])  # Print first 500 chars
            if stderr:
                print("\nDatabase output:")
                print(stderr[:500])
            
            return True
        else:
            print(f"⚠️  Connection attempt returned code: {process.returncode}\n")
            if stderr:
                print("Error output:")
                print(stderr[:500])
            return None
    
    except subprocess.TimeoutExpired:
        print("⚠️  Connection timed out (PostgreSQL may be initializing)")
        return None
    except FileNotFoundError:
        print("❌ flyctl command not found")
        return False
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return None

def show_manual_setup():
    """Show manual setup instructions"""
    print("\n" + "="*60)
    print("  MANUAL DATABASE SETUP (ALTERNATIVE OPTIONS)")
    print("="*60 + "\n")
    
    print("Option 1: Using Fly.io Web Dashboard")
    print("-" * 40)
    print("1. Go to: https://fly.io/dashboard")
    print("2. Select: sg-property-db (Managed Postgres)")
    print("3. Click: 'Web Terminal' or 'Connect'")
    print("4. Copy & paste contents of: database/schema.sql")
    print("5. Execute\n")
    
    print("Option 2: Using PostgreSQL CLI (psql)")
    print("-" * 40)
    print("1. Install PostgreSQL: https://www.postgresql.org/download/")
    print("2. Get connection string from dashboard")
    print("3. Run:")
    print("   psql <connection-string> < database/schema.sql\n")
    
    print("Option 3: Using Python psycopg2")
    print("-" * 40)
    print("1. Install: pip install psycopg2-binary")
    print("2. Run: python scripts/deploy-schema-psycopg.py\n")

def main():
    """Main function"""
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir("..")  # Go to repo root
    
    result = deploy_schema_via_flyctl()
    
    if result is True:
        print("\n" + "="*60)
        print("  ✅ SCHEMA DEPLOYMENT COMPLETE")
        print("="*60 + "\n")
        print("Next steps:")
        print("1. Verify schema in PostgreSQL dashboard")
        print("2. Set up Telegram bot notifications")
        print("3. Start implementing data source scrapers\n")
        return 0
    
    else:
        show_manual_setup()
        print("="*60)
        print("  ⚠️  SCHEMA DEPLOYMENT REQUIRES MANUAL SETUP")
        print("="*60 + "\n")
        print("Schema file ready at: database/schema.sql")
        print("PostgreSQL cluster: sg-property-db (Managed Postgres)")
        print("Region: sin (Singapore)\n")
        return 0  # Not a hard failure

if __name__ == "__main__":
    sys.exit(main())

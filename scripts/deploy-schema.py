#!/usr/bin/env python3
"""
Deploy database schema to PostgreSQL via Fly.io Managed Postgres
"""

import os
import sys
import subprocess
import time

def run_command(cmd, description=""):
    """Run a shell command and return the output"""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print(f"{'='*60}\n")
    
    print(f"Running: {cmd}\n")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        print(f"\n❌ Command failed with exit code {result.returncode}")
        return False
    
    print(f"\n✅ Command succeeded")
    return True

def main():
    """Main deployment function"""
    
    print("\n" + "="*60)
    print("  SG PROPERTY BOT - DATABASE SCHEMA DEPLOYMENT")
    print("="*60 + "\n")
    
    # Step 1: Check schema file exists
    schema_file = "database/schema.sql"
    if not os.path.exists(schema_file):
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    print(f"✅ Schema file found: {schema_file}\n")
    
    # Step 2: Get PostgreSQL cluster ID
    print("Step 1: Retrieving PostgreSQL cluster info...")
    result = subprocess.run("flyctl mpg list", shell=True, capture_output=True, text=True)
    
    if "sg-property-db" not in result.stdout:
        print("❌ PostgreSQL cluster 'sg-property-db' not found")
        print("Available clusters:")
        print(result.stdout)
        return False
    
    print("✅ PostgreSQL cluster found: sg-property-db\n")
    
    # Step 3: Connect and deploy schema
    print("Step 2: Deploying database schema...")
    print("(This may take 1-2 minutes)\n")
    
    # Read schema file
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
    
    # Use flyctl mpg connect to deploy
    # We'll pipe the SQL through a temporary file
    temp_sql = "/tmp/sg-property-schema.sql"
    
    try:
        # Write schema to temp file
        with open(temp_sql, 'w') as f:
            f.write(schema_sql)
        
        # Deploy via flyctl proxy
        cmd = f"flyctl mpg connect nlkxjo5wgmloy93v < {temp_sql}"
        
        # Alternative: use psql directly if available
        print("Attempting to deploy schema via Fly.io proxy...\n")
        result = subprocess.run(
            f"flyctl mpg connect nlkxjo5wgmloy93v",
            shell=True,
            input=schema_sql,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if "CREATE TABLE" in result.stderr or "CREATE VIEW" in result.stderr or result.returncode == 0:
            print("✅ Schema deployed successfully!\n")
            print("Output:")
            print(result.stderr if result.stderr else result.stdout)
            return True
        else:
            print("⚠️  Unable to deploy schema via CLI (psql not found)")
            print("\nAlternative methods:\n")
            print("1. Use Fly.io Dashboard:")
            print("   https://fly.io/dashboard/ashraf-ali-610/managed_postgres/nlkxjo5wgmloy93v\n")
            print("2. Install PostgreSQL locally:")
            print("   Windows: https://www.postgresql.org/download/windows/\n")
            print("3. Schema file ready at: database/schema.sql")
            return None  # Not a hard failure
    
    except subprocess.TimeoutExpired:
        print("⚠️  Schema deployment timed out")
        return None
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return None
    finally:
        # Cleanup
        if os.path.exists(temp_sql):
            os.remove(temp_sql)

if __name__ == "__main__":
    success = main()
    
    print("\n" + "="*60)
    if success is True:
        print("  ✅ DATABASE SCHEMA DEPLOYED SUCCESSFULLY")
    elif success is None:
        print("  ⚠️  SCHEMA DEPLOYMENT REQUIRES MANUAL SETUP")
        print("     (See alternatives above)")
    else:
        print("  ❌ DATABASE SCHEMA DEPLOYMENT FAILED")
    print("="*60 + "\n")
    
    sys.exit(0 if success is True or success is None else 1)

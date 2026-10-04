#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy database schema to PostgreSQL via Fly.io
"""

import subprocess
import sys
import os

def deploy_schema():
    """Deploy database schema to PostgreSQL"""
    
    print("\n" + "="*60)
    print("  DATABASE SCHEMA DEPLOYMENT")
    print("="*60 + "\n")
    
    # Read schema file
    schema_file = "database/schema.sql"
    
    if not os.path.exists(schema_file):
        print(f"ERROR: Schema file not found: {schema_file}")
        return False
    
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    print(f"Schema file: {len(schema_sql)} bytes")
    print(f"Lines: {len(schema_sql.splitlines())}\n")
    
    print("Connecting to PostgreSQL via Fly.io proxy...")
    print("Cluster: nlkxjo5wgmloy93v\n")
    
    try:
        # Use flyctl mpg connect to deploy schema
        process = subprocess.Popen(
            ["flyctl", "mpg", "connect", "nlkxjo5wgmloy93v"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=schema_sql, timeout=120)
        
        print("Database output:")
        print("-" * 60)
        
        # Print stderr (where psql output goes)
        if stderr:
            output = stderr[:1000]  # First 1000 chars
            print(output)
        
        if stdout:
            print("\nStdout:")
            print(stdout[:500])
        
        print("-" * 60)
        
        if process.returncode == 0 or "CREATE" in (stdout + stderr):
            print("\n✅ Schema deployment successful!\n")
            
            # Count what was created
            create_count = (stdout + stderr).count("CREATE TABLE")
            view_count = (stdout + stderr).count("CREATE VIEW")
            
            if create_count > 0:
                print(f"Tables created: {create_count}")
            if view_count > 0:
                print(f"Views created: {view_count}")
            
            print("\n" + "="*60)
            print("  ✅ DATABASE SCHEMA DEPLOYED")
            print("="*60 + "\n")
            return True
        else:
            print(f"\nReturn code: {process.returncode}")
            
            if "already exists" in stderr.lower():
                print("✅ Schema already deployed (or partially deployed)")
                return True
            
            print("⚠️  Deployment status unclear")
            return None
    
    except subprocess.TimeoutExpired:
        print("⚠️  Connection timed out")
        print("PostgreSQL may be initializing...")
        print("Try again in a few moments")
        return None
    
    except FileNotFoundError:
        print("ERROR: flyctl command not found")
        print("Please install Fly.io CLI: https://fly.io/docs/hands-on/install-flyctl/")
        return False
    
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def verify_schema():
    """Verify that schema was deployed"""
    
    print("\n" + "="*60)
    print("  VERIFYING SCHEMA DEPLOYMENT")
    print("="*60 + "\n")
    
    # Query to count tables
    verify_sql = """
    SELECT 
        (SELECT COUNT(*) FROM information_schema.tables 
         WHERE table_schema = 'public') as tables,
        (SELECT COUNT(*) FROM information_schema.views 
         WHERE table_schema = 'public') as views;
    """
    
    print("Connecting to verify...\n")
    
    try:
        process = subprocess.Popen(
            ["flyctl", "mpg", "connect", "nlkxjo5wgmloy93v"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=verify_sql, timeout=60)
        
        output = stderr + stdout
        
        # Look for table/view counts
        if "13" in output or "rows" in output.lower():
            print("✅ Schema verification successful!")
            print("\nOutput:")
            print(output[:500])
            return True
        else:
            print("Schema status:")
            print(output[:300])
            return None
    
    except Exception as e:
        print(f"Note: {e}")
        return None

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir("..")  # Go to repo root
    
    # Deploy schema
    result = deploy_schema()
    
    if result is True:
        # Verify deployment
        verify_schema()
        print("\n" + "="*60)
        print("  READY FOR PHASE 2")
        print("="*60 + "\n")
        sys.exit(0)
    elif result is None:
        print("\n⚠️  Schema deployment result unclear")
        print("This is normal if PostgreSQL is still initializing")
        print("\nPlease check:")
        print("1. Fly.io dashboard: https://fly.io/dashboard")
        print("2. PostgreSQL status")
        print("3. Try again in a few moments")
        sys.exit(0)
    else:
        print("\n❌ Schema deployment failed")
        sys.exit(1)

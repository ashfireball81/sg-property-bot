#!/usr/bin/env python3
"""
Direct schema deployment to Fly.io PostgreSQL without GitHub Actions
Uses Fly.io API to connect directly to the database
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()

def deploy_schema():
    """Deploy schema directly via Fly.io SSH or API"""
    
    print("\n" + "="*70)
    print("  🚀 SG PROPERTY BOT - DIRECT SCHEMA DEPLOYMENT")
    print("="*70 + "\n")
    
    # Read schema file
    schema_file = Path(__file__).parent / "database" / "schema.sql"
    
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    print(f"📄 Loading schema: {schema_file}")
    schema_content = schema_file.read_text(encoding='utf-8')
    print(f"   ✓ Size: {len(schema_content):,} bytes")
    print(f"   ✓ Lines: {len(schema_content.splitlines())}")
    print()
    
    # Try method 1: Using flyctl SSH
    print("Method 1️⃣  : Deploying via flyctl SSH (secure tunnel)")
    print("-" * 70)
    print()
    
    # Create temp file with schema (handle Windows temp path)
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_schema = Path(temp_dir) / "schema.sql"
    temp_schema.write_text(schema_content, encoding='utf-8')
    print(f"✓ Wrote schema to temp file: {temp_schema}")
    print()
    
    # Try to connect via flyctl
    print("🔗 Connecting to Fly.io PostgreSQL...")
    print("   Cluster: nlkxjo5wgmloy93v (sg-property-db)")
    print()
    
    # Check if flyctl is available
    flyctl_check = run_command("flyctl --version", check=False)
    if not flyctl_check:
        print("❌ flyctl not found")
        print()
        return deploy_via_api()
    
    print(f"✓ flyctl version: {flyctl_check}")
    print()
    
    # Method 1: Use flyctl mpg connect with psql
    print("⏳ Attempting psql deployment via flyctl...")
    print()
    
    # Try to get DATABASE_URL from fly.io secrets
    print("Getting DATABASE_URL from Fly.io secrets...")
    secrets_cmd = "flyctl secrets list -a sg-property-bot --json 2>/dev/null"
    secrets_output = run_command(secrets_cmd, check=False)
    
    if secrets_output:
        try:
            secrets_json = json.loads(secrets_output)
            db_url = next((s['Value'] for s in secrets_json if s['Name'] == 'DATABASE_URL'), None)
            
            if db_url:
                print(f"✓ Found DATABASE_URL")
                print()
                
                # Try psql if available
                psql_check = run_command("psql --version", check=False)
                if psql_check:
                    print(f"✓ psql available: {psql_check}")
                    print()
                    print("⏳ Deploying schema with psql...")
                    
                    # Deploy using psql
                    deploy_cmd = f"psql '{db_url}' -f {temp_schema} 2>&1"
                    output = run_command(deploy_cmd, check=False)
                    
                    if output and "ERROR" not in output.upper():
                        print("✅ SCHEMA DEPLOYED SUCCESSFULLY!")
                        print()
                        print(output[-500:] if len(output) > 500 else output)
                        return True
                    else:
                        print("⚠️ psql deployment encountered issues")
                        if output:
                            print(output[-300:])
                        print()
                else:
                    print("⚠️ psql not available locally")
                    print()
                    print("Attempting via flyctl postgres connect...")
                    
                    # Use flyctl to execute
                    connect_cmd = f"cat {temp_schema} | flyctl postgres connect nlkxjo5wgmloy93v 2>&1"
                    output = run_command(connect_cmd, check=False)
                    
                    if output and "CREATE TABLE" in output:
                        print("✅ SCHEMA DEPLOYED SUCCESSFULLY!")
                        print()
                        return True
                    else:
                        print("⚠️ Connection attempt output:")
                        print(output[-300:] if output and len(output) > 300 else output)
                        print()
        except Exception as e:
            print(f"⚠️ Error parsing secrets: {e}")
            print()
    else:
        print("⚠️ Could not retrieve secrets from Fly.io")
        print()
    
    return deploy_via_docker()

def deploy_via_docker():
    """Deploy using Docker PostgreSQL client"""
    
    print()
    print("Method 2️⃣  : Deploying via Docker PostgreSQL image")
    print("-" * 70)
    print()
    
    # Try to use Docker postgres image
    print("Checking Docker availability...")
    docker_check = run_command("docker --version", check=False)
    
    if not docker_check:
        print("❌ Docker not available")
        print()
        return deploy_via_python()
    
    print(f"✓ Docker available: {docker_check}")
    print()
    
    # Get DATABASE_URL
    secrets_cmd = "flyctl secrets list -a sg-property-bot --json 2>/dev/null"
    secrets_output = run_command(secrets_cmd, check=False)
    
    if secrets_output:
        try:
            secrets_json = json.loads(secrets_output)
            db_url = next((s['Value'] for s in secrets_json if s['Name'] == 'DATABASE_URL'), None)
            
            if db_url:
                print(f"✓ Found DATABASE_URL")
                print("⏳ Deploying via Docker...")
                print()
                
                schema_file = Path(__file__).parent / "database" / "schema.sql"
                docker_cmd = (
                    f"docker run --rm "
                    f"-e PGPASSWORD=$(echo '{db_url}' | cut -d: -f3 | cut -d@ -f1) "
                    f"-v {schema_file}:/schema.sql "
                    f"postgres:latest "
                    f"psql -h $(echo '{db_url}' | cut -d: -f2 | tr -d '/') "
                    f"-U $(echo '{db_url}' | cut -d: -f1 | cut -d'/' -f4) "
                    f"-d $(echo '{db_url}' | cut -d'/' -f4) "
                    f"-f /schema.sql"
                )
                
                output = run_command(docker_cmd, check=False)
                
                if output and "CREATE TABLE" in output:
                    print("✅ SCHEMA DEPLOYED SUCCESSFULLY!")
                    return True
                else:
                    print("⚠️ Docker deployment had issues")
                    if output:
                        print(output[-300:])
                    print()
        except Exception as e:
            print(f"⚠️ Error: {e}")
            print()
    
    return deploy_via_python()

def deploy_via_python():
    """Deploy using Python psycopg2"""
    
    print()
    print("Method 3️⃣  : Deploying via Python psycopg2")
    print("-" * 70)
    print()
    
    try:
        import psycopg2
        print("✓ psycopg2 available")
    except ImportError:
        print("❌ psycopg2 not installed")
        print("   Installing psycopg2...")
        run_command(f"{sys.executable} -m pip install psycopg2-binary -q", check=False)
        
        try:
            import psycopg2
            print("✓ psycopg2 installed")
        except ImportError:
            print("❌ Could not install psycopg2")
            print()
            return print_final_instructions()
    
    print()
    print("Getting DATABASE_URL from Fly.io...")
    
    # Get secrets
    secrets_cmd = "flyctl secrets list -a sg-property-bot --json 2>/dev/null"
    secrets_output = run_command(secrets_cmd, check=False)
    
    if not secrets_output:
        print("❌ Could not retrieve secrets")
        print()
        return print_final_instructions()
    
    try:
        secrets_json = json.loads(secrets_output)
        db_url = next((s['Value'] for s in secrets_json if s['Name'] == 'DATABASE_URL'), None)
        
        if not db_url:
            print("❌ DATABASE_URL not found in secrets")
            print()
            return print_final_instructions()
        
        print(f"✓ Found DATABASE_URL")
        print()
        print("⏳ Connecting to PostgreSQL...")
        
        import psycopg2
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("✓ Connected!")
        print()
        print("⏳ Executing schema SQL...")
        
        schema_file = Path(__file__).parent / "database" / "schema.sql"
        schema_content = schema_file.read_text(encoding='utf-8')
        
        cursor.execute(schema_content)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ SCHEMA DEPLOYED SUCCESSFULLY!")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        return print_final_instructions()

def print_final_instructions():
    """Print manual deployment instructions"""
    
    print()
    print("="*70)
    print("  ⚠️  AUTOMATED DEPLOYMENT NOT POSSIBLE")
    print("="*70)
    print()
    print("All automated methods failed. Please deploy manually using one of these:")
    print()
    print("OPTION 1: Fly.io Web Terminal (Recommended)")
    print("  1. Go to: https://fly.io/dashboard")
    print("  2. Click: sg-property-db")
    print("  3. Tab: 'Web Terminal'")
    print("  4. Copy: database/schema.sql")
    print("  5. Paste and press Enter")
    print()
    print("OPTION 2: GitHub Actions")
    print("  1. Go to: https://github.com/ashfireball81/GeneralBot/actions")
    print("  2. Click: Deploy Database Schema")
    print("  3. Click: Run workflow")
    print("  (Note: Requires FLY_API_TOKEN secret to be set)")
    print()
    return False

def main():
    try:
        result = deploy_schema()
        
        if result:
            print()
            print("="*70)
            print("  🎉 PHASE 1 COMPLETE - READY FOR PHASE 2!")
            print("="*70)
            print()
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

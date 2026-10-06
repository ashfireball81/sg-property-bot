#!/usr/bin/env python3
"""
Fly.io Deployment Automation Script
Deploys sg-property-bot with database to Fly.io
"""

import subprocess
import os
import sys
from pathlib import Path


class FlyDeployment:
    def __init__(self):
        self.app_name = "sg-property-bot"
        self.db_app_name = "sg-property-bot-db"
        self.region = "sin"  # Singapore
        
    def run_command(self, cmd, description, check=True):
        """Run shell command and handle errors"""
        print(f"\n🔄 {description}...")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            
            if result.stdout:
                print(result.stdout.strip())
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, "", str(e)
    
    def check_authentication(self):
        """Check if user is authenticated to Fly.io"""
        print("\n" + "="*70)
        print("                    FLY.IO DEPLOYMENT AUTOMATION")
        print("="*70)
        
        print("\n📋 Step 1: Checking Fly.io authentication...")
        
        success, output, _ = self.run_command(
            "flyctl auth whoami",
            "Checking authentication",
            check=False
        )
        
        if not success:
            print("\n❌ Not logged in to Fly.io")
            print("\nPlease login first:")
            print("  flyctl auth login")
            print("\nThen run this script again.")
            return False
        
        print(f"✅ Authenticated as: {output.strip()}")
        return True
    
    def check_app_exists(self):
        """Check if app exists on Fly.io"""
        print(f"\n📋 Step 2: Checking if app '{self.app_name}' exists...")
        
        success, output, _ = self.run_command(
            f"flyctl apps info {self.app_name}",
            "Checking app status",
            check=False
        )
        
        if success:
            print(f"✅ App '{self.app_name}' exists")
            return True
        else:
            print(f"⚠️  App '{self.app_name}' not found")
            return False
    
    def create_app(self):
        """Create Fly.io app"""
        print(f"\n📋 Step 3: Creating app '{self.app_name}'...")
        
        success, output, error = self.run_command(
            f"flyctl app create {self.app_name} --region {self.region}",
            f"Creating app",
            check=False
        )
        
        if success:
            print(f"✅ App created successfully")
            return True
        else:
            if "already exists" in error:
                print(f"✅ App already exists")
                return True
            else:
                print(f"❌ Failed to create app: {error}")
                return False
    
    def check_postgres_cluster(self):
        """Check if PostgreSQL cluster exists"""
        print(f"\n📋 Step 4: Checking PostgreSQL cluster...")
        
        success, output, _ = self.run_command(
            f"flyctl postgres list",
            "Listing PostgreSQL clusters",
            check=False
        )
        
        if self.db_app_name in output:
            print(f"✅ PostgreSQL cluster '{self.db_app_name}' exists")
            return True
        else:
            print(f"⚠️  PostgreSQL cluster not found")
            return False
    
    def create_postgres_cluster(self):
        """Create PostgreSQL cluster"""
        print(f"\n📋 Step 5: Creating PostgreSQL cluster...")
        
        success, output, error = self.run_command(
            f"flyctl postgres create --app {self.app_name} --region {self.region} --vm-size shared-cpu-1x",
            "Creating PostgreSQL cluster",
            check=False
        )
        
        if success or "already exists" in error:
            print(f"✅ PostgreSQL cluster ready")
            return True
        else:
            print(f"❌ Failed to create PostgreSQL: {error}")
            return False
    
    def get_db_credentials(self):
        """Get database connection details"""
        print(f"\n📋 Step 6: Getting database credentials...")
        
        success, output, _ = self.run_command(
            f"flyctl postgres info --app {self.db_app_name}",
            "Retrieving database info",
            check=False
        )
        
        if success:
            print("Database info retrieved")
            print(output)
            return True
        else:
            print("Could not retrieve database info")
            return False
    
    def set_secrets(self):
        """Set Fly.io secrets from environment"""
        print(f"\n📋 Step 7: Setting Fly.io secrets...")
        
        # Load from .env
        env_file = Path(".env")
        if not env_file.exists():
            print("❌ .env file not found")
            return False
        
        # Read secrets
        secrets = {}
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    secrets[key] = value
        
        # Add database secrets
        print("\nDatabase connection details needed:")
        db_host = input("  DB_HOST (e.g., sg-property-bot-db.internal): ").strip()
        db_port = input("  DB_PORT (default 5432): ").strip() or "5432"
        db_name = input("  DB_NAME (e.g., propertybot): ").strip() or "propertybot"
        db_user = input("  DB_USER (default postgres): ").strip() or "postgres"
        db_password = input("  DB_PASSWORD: ").strip()
        
        # Set secrets
        all_secrets = {
            "DB_HOST": db_host or "sg-property-bot-db.internal",
            "DB_PORT": db_port,
            "DB_NAME": db_name,
            "DB_USER": db_user,
            "DB_PASSWORD": db_password,
            "TELEGRAM_BOT_TOKEN": secrets.get("TELEGRAM_BOT_TOKEN", ""),
            "TELEGRAM_CHAT_ID": secrets.get("TELEGRAM_CHAT_ID", ""),
        }
        
        secrets_str = " ".join([f'{k}="{v}"' for k, v in all_secrets.items() if v])
        
        success, output, _ = self.run_command(
            f'flyctl secrets set {secrets_str} --app {self.app_name}',
            "Setting secrets",
            check=False
        )
        
        if success:
            print("✅ Secrets set successfully")
            return True
        else:
            print("⚠️  Could not set all secrets (you can set them manually)")
            print(f"Command: flyctl secrets set {secrets_str} --app {self.app_name}")
            return True
    
    def deploy_app(self):
        """Deploy app to Fly.io"""
        print(f"\n📋 Step 8: Deploying app to Fly.io...")
        
        success, output, error = self.run_command(
            f"flyctl deploy --app {self.app_name}",
            "Deploying app",
            check=False
        )
        
        if success:
            print("✅ App deployed successfully")
            return True
        else:
            print(f"❌ Deployment failed: {error}")
            return False
    
    def check_app_status(self):
        """Check deployed app status"""
        print(f"\n📋 Step 9: Checking app status...")
        
        success, output, _ = self.run_command(
            f"flyctl status --app {self.app_name}",
            "Checking status",
            check=False
        )
        
        if success:
            print(output)
            return True
        else:
            print("Could not check status")
            return False
    
    def display_summary(self, success):
        """Display deployment summary"""
        print("\n" + "="*70)
        
        if success:
            print("                    ✅ DEPLOYMENT COMPLETE")
        else:
            print("                    ⚠️  DEPLOYMENT PARTIAL")
        
        print("="*70)
        
        print("\nNext Steps:")
        print("1. Verify deployment:")
        print(f"   flyctl status --app {self.app_name}")
        print("\n2. View logs:")
        print(f"   flyctl logs --app {self.app_name} --follow")
        print("\n3. Connect to database:")
        print(f"   flyctl postgres connect --app {self.db_app_name}")
        print("\n4. Create scheduled job:")
        print(f"   flyctl machines create --app {self.app_name} \\")
        print('     --schedule cron="0 22 * * *" \\')
        print("     python orchestrator_v3.py")
        print("\n5. Test full pipeline:")
        print(f"   flyctl ssh console --app {self.app_name}")
        print("   python orchestrator_v3.py")
        print("\n" + "="*70 + "\n")
    
    def run(self):
        """Run complete deployment"""
        
        if not self.check_authentication():
            return False
        
        # Check/create app
        if not self.check_app_exists():
            if not self.create_app():
                return False
        
        # Check/create database
        if not self.check_postgres_cluster():
            if not self.create_postgres_cluster():
                print("⚠️  Database creation may require manual steps")
        
        # Get database info
        self.get_db_credentials()
        
        # Set secrets
        if not self.set_secrets():
            return False
        
        # Deploy app
        if not self.deploy_app():
            return False
        
        # Check status
        self.check_app_status()
        
        self.display_summary(True)
        return True


def main():
    """Main entry point"""
    deployer = FlyDeployment()
    
    try:
        success = deployer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

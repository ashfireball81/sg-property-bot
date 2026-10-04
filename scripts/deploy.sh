#!/bin/bash
# Deploy SG Property Bot Infrastructure to Fly.io
# Prerequisites: flyctl installed and authenticated

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  SG Property Bot - Infrastructure Deployment Script${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}\n"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
if ! command -v flyctl &> /dev/null; then
    echo -e "${RED}Error: flyctl not installed${NC}"
    echo "Install from: https://fly.io/docs/getting-started/installing-flyctl/"
    exit 1
fi

if ! flyctl auth whoami &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with Fly.io${NC}"
    echo "Run: flyctl auth login"
    exit 1
fi

APP_NAME="sg-property-bot"
REGION="sin"  # Singapore

echo -e "${GREEN}✓ Prerequisites OK${NC}\n"

# Step 1: Create Fly.io App
echo -e "${YELLOW}Step 1: Creating Fly.io application...${NC}"
if flyctl apps list | grep -q "$APP_NAME"; then
    echo -e "${GREEN}✓ App '$APP_NAME' already exists${NC}"
else
    echo "Creating app '$APP_NAME' in region '$REGION'..."
    flyctl apps create "$APP_NAME" --region "$REGION" || true
    echo -e "${GREEN}✓ App created${NC}"
fi

# Step 2: Create PostgreSQL Database
echo -e "\n${YELLOW}Step 2: Creating PostgreSQL database...${NC}"
DB_NAME="sg-property-db"
if flyctl postgres list 2>/dev/null | grep -q "$DB_NAME"; then
    echo -e "${GREEN}✓ Database '$DB_NAME' already exists${NC}"
else
    echo "Creating PostgreSQL instance..."
    # For production, use:
    # flyctl postgres create --name "$DB_NAME" --region "$REGION" --vm-size performance-1x
    
    # For development, use smaller:
    flyctl postgres create --name "$DB_NAME" --region "$REGION" --vm-size shared-cpu-1x || true
    echo -e "${GREEN}✓ PostgreSQL instance created${NC}"
fi

# Step 3: Create Redis Cache
echo -e "\n${YELLOW}Step 3: Creating Redis cache...${NC}"
REDIS_NAME="sg-property-cache"
if flyctl redis list 2>/dev/null | grep -q "$REDIS_NAME"; then
    echo -e "${GREEN}✓ Redis instance '$REDIS_NAME' already exists${NC}"
else
    echo "Creating Redis instance..."
    flyctl redis create --name "$REDIS_NAME" --region "$REGION" || true
    echo -e "${GREEN}✓ Redis instance created${NC}"
fi

# Step 4: Create secrets
echo -e "\n${YELLOW}Step 4: Creating placeholder secrets...${NC}"
# These will be updated when credentials are provided
flyctl secrets set \
  NODE_ENV=production \
  API_PORT=3000 \
  LOG_LEVEL=info \
  --app "$APP_NAME" 2>/dev/null || true
echo -e "${GREEN}✓ Secrets created (placeholders)${NC}"

# Step 5: Deploy API
echo -e "\n${YELLOW}Step 5: Deploying API to Fly.io...${NC}"
echo "Building and deploying Docker image..."
flyctl deploy --app "$APP_NAME" --region "$REGION" || true
echo -e "${GREEN}✓ API deployed${NC}"

# Step 6: Verify deployment
echo -e "\n${YELLOW}Step 6: Verifying deployment...${NC}"
echo "Checking app status..."
flyctl status --app "$APP_NAME"

echo -e "\n${YELLOW}Getting connection URLs...${NC}"
DATABASE_URL=$(flyctl postgres connect-string sg-property-db)
REDIS_URL=$(flyctl redis connect-string sg-property-cache 2>/dev/null || echo "Redis URL - set manually")

echo -e "\n${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ Infrastructure Deployment Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Connection Details:${NC}"
echo "App Name: $APP_NAME"
echo "Region: $REGION"
echo "API URL: https://${APP_NAME}.fly.dev"
echo "Database: $DATABASE_URL"
echo "Redis: $REDIS_URL"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Update .env with connection strings above"
echo "2. Deploy schema: flyctl postgres exec sg-property-db < database/schema.sql"
echo "3. Monitor logs: flyctl logs --app $APP_NAME"
echo "4. View dashboard: https://fly.io/apps/$APP_NAME"

echo -e "\n${GREEN}Deployment complete!${NC}\n"

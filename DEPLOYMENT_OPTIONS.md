# CES Dashboard Deployment Options

## Option 1: Vercel (Recommended - Fastest)

### Steps:
1. **Login to Vercel:**
   ```bash
   vercel login
   ```
   - Choose "Continue with Email"
   - Use your personal email

2. **Deploy:**
   ```bash
   rm -rf .vercel
   vercel --prod --yes
   ```

### Vercel Benefits:
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Zero configuration
- ✅ Free tier available

---

## Option 2: Azure App Service (Fallback)

### Prerequisites:
- Azure CLI installed: `brew install azure-cli`
- Azure account with active subscription

### Steps:

1. **Login to Azure:**
   ```bash
   az login
   ```

2. **Create deployment package:**
   ```bash
   # Build the app
   npm run build
   
   # Copy web.config to dist folder
   cp web.config dist/
   
   # Create deployment zip
   cd dist && zip -r ../deploy.zip . && cd ..
   ```

3. **Create Azure resources:**
   ```bash
   # Variables
   RESOURCE_GROUP="ces-dashboard-rg"
   APP_NAME="ces-dashboard-$(date +%s)"
   LOCATION="eastus"
   
   # Create resource group
   az group create --name $RESOURCE_GROUP --location $LOCATION
   
   # Create App Service plan (Free tier)
   az appservice plan create \
     --name "${APP_NAME}-plan" \
     --resource-group $RESOURCE_GROUP \
     --sku F1 \
     --is-linux false
   
   # Create Web App
   az webapp create \
     --name $APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --plan "${APP_NAME}-plan"
   ```

4. **Deploy:**
   ```bash
   # Deploy the zip file
   az webapp deployment source config-zip \
     --resource-group $RESOURCE_GROUP \
     --name $APP_NAME \
     --src deploy.zip
   
   # Get the URL
   echo "Your app is deployed at: https://${APP_NAME}.azurewebsites.net"
   ```

### Azure Benefits:
- ✅ No authentication walls
- ✅ Free tier available (60 min/day)
- ✅ Integrates with Azure services

---

## Quick Deploy Script

Save this as `deploy.sh`:

```bash
#!/bin/bash

echo "Choose deployment platform:"
echo "1) Vercel"
echo "2) Azure App Service"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo "Deploying to Vercel..."
    rm -rf .vercel
    vercel --prod --yes
elif [ "$choice" = "2" ]; then
    echo "Deploying to Azure..."
    
    # Build
    npm run build
    cp web.config dist/
    cd dist && zip -r ../deploy.zip . && cd ..
    
    # Deploy
    RESOURCE_GROUP="ces-dashboard-rg"
    APP_NAME="ces-dashboard-$(date +%s)"
    
    az group create --name $RESOURCE_GROUP --location eastus
    az appservice plan create --name "${APP_NAME}-plan" --resource-group $RESOURCE_GROUP --sku F1
    az webapp create --name $APP_NAME --resource-group $RESOURCE_GROUP --plan "${APP_NAME}-plan"
    az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src deploy.zip
    
    echo "Deployed to: https://${APP_NAME}.azurewebsites.net"
else
    echo "Invalid choice"
fi
```

---

## What's Already Fixed

✅ **Preload warnings eliminated:**
- `modulePreload: false` in vite.config.ts
- Single bundle output
- No modulepreload links

✅ **Build optimized:**
- Single 678KB JavaScript file
- Fast loading
- Proper caching headers

## Verification

After deployment to either platform:
1. Open browser console (F12)
2. Check for no preload warnings
3. Verify dashboard loads correctly
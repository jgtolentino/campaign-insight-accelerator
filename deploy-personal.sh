#!/bin/bash

echo "=== CES Dashboard Personal Deployment Script ==="
echo ""
echo "This script will help you deploy to your personal Vercel account"
echo ""

# Check if logged in
if ! vercel whoami &>/dev/null; then
    echo "📋 You need to login to Vercel first"
    echo "👉 Please run: vercel login"
    echo "   Choose 'Continue with Email' and use your personal account"
    echo ""
    echo "After logging in, run this script again: ./deploy-personal.sh"
    exit 1
fi

# Show current user
echo "✅ Logged in as: $(vercel whoami)"
echo ""

# Remove existing project link
rm -rf .vercel

# Deploy
echo "🚀 Deploying to your personal account..."
echo ""

# Deploy without team scope
vercel --prod --yes --name="ces-dashboard-free"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🎉 Your dashboard should now be accessible without authentication!"
# Deploy CES Dashboard to Personal Vercel Account

## Quick Deploy (Recommended)

1. **Login to your personal Vercel account:**
   ```bash
   vercel login
   ```
   - Choose "Continue with Email"
   - Use your personal email (not team email)

2. **Deploy the dashboard:**
   ```bash
   ./deploy-personal.sh
   ```

## Manual Deploy

If the script doesn't work, use these commands:

1. **Login to Vercel:**
   ```bash
   vercel login
   ```

2. **Remove old project link:**
   ```bash
   rm -rf .vercel
   ```

3. **Deploy to your personal account:**
   ```bash
   vercel --prod --yes
   ```
   - When prompted for scope, choose your personal account (not team)
   - Project name: `ces-dashboard` (or any name you prefer)

## What's Fixed

✅ **Preload warnings**: Completely eliminated by disabling modulePreload
✅ **Single bundle**: No more multiple chunks causing warnings
✅ **Optimized build**: Fast loading with single 678KB bundle

## Build Details

The optimized build configuration:
- Disabled module preloading (`modulePreload: false`)
- Single JavaScript bundle instead of multiple chunks
- No `<link rel="modulepreload">` tags in HTML
- Proper caching headers configured

## Verify Success

After deployment, check:
1. No "resource was preloaded" warnings in console
2. Dashboard loads without authentication prompt
3. All functionality works correctly

## Troubleshooting

If you see authentication page:
- Make sure you're logged into your personal account: `vercel whoami`
- Ensure you didn't select a team account during deployment
- Try creating a new project name if reusing an existing one

## Local Testing

To test locally before deploying:
```bash
npm run build
npm run preview
```
Open http://localhost:4173 to verify everything works.
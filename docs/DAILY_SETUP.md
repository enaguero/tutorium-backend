# Daily.co Setup Guide

This guide will help you set up your Daily.co account and obtain the necessary API credentials.

## Step 1: Create a Daily.co Account

1. Visit https://dashboard.daily.co/signup
2. Sign up with your email or GitHub account
3. Verify your email address

## Step 2: Get Your API Key

Once logged in to the Daily.co dashboard:

1. Navigate to the **Developers** section in the left sidebar
2. Click on **API Keys**
3. You'll see your **API Key** displayed
4. Click the **Copy** button to copy your API key

**Important**: Keep this key secure! It's like a password for your Daily.co account.

## Step 3: Get Your Domain Name

1. In the Daily.co dashboard, look at the top-left corner
2. You'll see your domain name (e.g., `your-company.daily.co`)
3. Copy this domain name

## Step 4: Set Up Webhook Secret (Optional for Phase 1)

If you plan to use webhooks:

1. Go to **Developers** → **Webhooks**
2. Click **Create webhook**
3. Enter your backend URL (e.g., `https://your-backend.com/api/v1/webhooks/daily`)
4. Copy the **Webhook secret** that's generated

For local development, you can skip this for now.

## Step 5: Update Your .env File

1. Copy `.env.example` to `.env` if you haven't already:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and update the Daily.co values:
   ```bash
   # Daily.co Integration
   DAILY_API_KEY=a1b2c3d4e5f6g7h8i9j0  # Your actual API key from Step 2
   DAILY_DOMAIN=your-company.daily.co    # Your domain from Step 3
   DAILY_WEBHOOK_SECRET=webhook_secret   # Your webhook secret from Step 4 (optional)
   DAILY_API_BASE_URL=https://api.daily.co/v1
   ```

3. Save the file

## Step 6: Verify Configuration

You can verify your configuration is working by running a simple test:

```bash
# Activate your virtual environment
source .venv/bin/activate

# Start Python
python

# Test the configuration
from app.core.config import settings
print(f"Daily API Key set: {bool(settings.DAILY_API_KEY)}")
print(f"Daily Domain: {settings.DAILY_DOMAIN}")
```

You should see:
```
Daily API Key set: True
Daily Domain: your-company.daily.co
```

## Daily.co Free Tier Limits

The free tier includes:
- **10,000 minutes/month** of video call time
- Perfect for development and testing
- Up to 10 participants per call
- No credit card required

For production, you may need to upgrade to:
- **Starter**: $9/month for 100K minutes
- **Scale**: Custom pricing for higher volumes

## Security Best Practices

1. ✅ **Never commit your `.env` file** to version control
2. ✅ Keep your API key secret - don't share it or expose it in frontend code
3. ✅ Use environment variables for production deployment
4. ✅ Rotate your API keys periodically
5. ✅ Use webhook secrets to verify webhook authenticity

## Troubleshooting

### "Invalid API key" error
- Double-check you copied the entire API key
- Make sure there are no extra spaces before/after the key
- Verify the key is active in your Daily.co dashboard

### Can't find your domain
- Look in the top-left corner of the Daily.co dashboard
- It should be in the format: `yourname.daily.co`
- You can also find it under **Account Settings**

### Domain doesn't work
- If you want a custom domain, you need to upgrade your plan
- For development, the default `yourname.daily.co` domain works fine

## Next Steps

Once you have your credentials set up:

1. ✅ Configuration is complete!
2. ⏭️ Continue to Step 2 of the implementation plan: **Database Models**
3. 📖 Refer to `docs/features/02-phase-2-daily-implementation-plan.md` for the full implementation guide

## Additional Resources

- [Daily.co API Documentation](https://docs.daily.co/reference/rest-api)
- [Daily.co Dashboard](https://dashboard.daily.co/)
- [Daily.co Pricing](https://www.daily.co/pricing)
- [Daily.co Support](https://help.daily.co/)

## Quick Reference

### Environment Variables
```bash
DAILY_API_KEY=<your-api-key>
DAILY_DOMAIN=<your-domain>.daily.co
DAILY_WEBHOOK_SECRET=<webhook-secret>  # Optional
DAILY_API_BASE_URL=https://api.daily.co/v1
```

### Testing Your Setup
```bash
# Test API key is valid
curl -H "Authorization: Bearer $DAILY_API_KEY" https://api.daily.co/v1/
```

You should get a response like: `{"info": "Daily.co API"}`

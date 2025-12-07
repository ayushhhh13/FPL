# How to Enable GCP Billing for Speech-to-Text API

## Quick Link
**Direct link to enable billing:**
https://console.developers.google.com/billing/enable?project=228094933169

## Step-by-Step Instructions

### Method 1: Direct Link (Fastest)
1. Click or copy this link: https://console.developers.google.com/billing/enable?project=228094933169
2. Sign in with your Google account (the one that has access to the GCP project)
3. Follow the prompts to enable billing
4. Wait 2-5 minutes for changes to propagate

### Method 2: Manual Steps

#### Step 1: Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Sign in with your Google account

#### Step 2: Select Your Project
- Click the project dropdown at the top
- Select project ID: **228094933169** (or your project name)

#### Step 3: Navigate to Billing
- Click the hamburger menu (☰) in the top left
- Go to **Billing** → **Account Management**
- Or directly visit: https://console.cloud.google.com/billing

#### Step 4: Link Billing Account
- If you don't have a billing account:
  - Click **"Create Billing Account"**
  - Fill in your payment information
  - Accept the terms
- If you have a billing account:
  - Click **"Link a Billing Account"**
  - Select your existing billing account
  - Click **"Set Account"**

#### Step 5: Verify Billing is Enabled
- Go to: https://console.cloud.google.com/apis/api/speech.googleapis.com/overview?project=228094933169
- Check that the API shows as "Enabled"
- Status should show billing is active

#### Step 6: Wait for Propagation
- After enabling billing, wait **2-5 minutes**
- The changes need to propagate through Google's systems
- Try the voice input again after waiting

## Important Notes

### Free Tier
- Google Cloud Speech-to-Text has a **free tier**:
  - First 60 minutes of audio per month are FREE
  - After that, it's pay-as-you-go
  - No credit card required for free tier (in some regions)

### Billing Account Requirements
- You need a valid payment method (credit card, debit card, or bank account)
- Google will verify your payment method
- You can set up billing alerts to avoid unexpected charges

### Cost Information
- Speech-to-Text pricing: ~$0.006 per 15 seconds (after free tier)
- For testing/development, you'll likely stay within free tier
- Set up billing alerts at: https://console.cloud.google.com/billing/budgets

## Verify It's Working

After enabling billing, test with:

```bash
cd /Users/ayush/Downloads/FPL
source venv/bin/activate
python test_gcp_speech.py
```

You should see:
- Status Code: 200 (instead of 403)
- Success message instead of billing error

## Troubleshooting

### If billing is enabled but still getting 403:
1. Wait 5-10 minutes (propagation delay)
2. Check API is enabled: https://console.cloud.google.com/apis/api/speech.googleapis.com/overview
3. Verify project ID matches in .env file
4. Check billing account is linked to the project

### If you don't have access:
- Contact the project owner/administrator
- Request billing account access
- Or create a new GCP project with your own billing

## Alternative: Use a Different Speech-to-Text Service

If you can't enable billing, you could:
1. Use OpenAI Whisper API (requires OpenAI API key)
2. Use Azure Speech Services
3. Use AWS Transcribe
4. Use a local speech recognition library

Let me know if you'd like help setting up an alternative!


# Setup Guide

## Prerequisites

- Python 3.8 or higher
- Autodesk Platform Services (APS) account
- OpenAI, Anthropic, or Gemini API key

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Autodesk Platform Services

1. Go to https://aps.autodesk.com/
2. Create a new app
3. Note your Client ID and Client Secret
4. Set up OAuth redirect URLs (e.g., `http://localhost:8080/callback`)

## Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   APS_CLIENT_ID=your_client_id_here
   APS_CLIENT_SECRET=your_client_secret_here
   APS_CALLBACK_URL=http://localhost:8080/callback
   
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   # OR
   GEMINI_API_KEY=your_gemini_api_key_here  # alias: GOOGLE_API_KEY
   ```

## Step 4: Test Installation

Run the demo script:
```bash
python examples/demo.py --project-id <your_project_id> --design-id <your_design_id> --intent "Minimize weight" --dry-run
```

## Troubleshooting

### Authentication Errors
- Verify your APS credentials are correct
- Check that OAuth redirect URLs match
- Ensure scopes include `data:read`, `data:write`, `code:all`

### API Errors
- Verify Fusion 360 API endpoints are correct for your APS version
- Check that your project and design IDs are valid
- Ensure you have proper permissions on the project

### AI Provider Errors
- Verify API keys are set correctly
- Check API quota/limits
- Ensure the model name is valid for your provider


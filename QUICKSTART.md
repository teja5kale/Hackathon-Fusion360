# Quick Start Guide

Get up and running with AI-Assisted Parametric Design Automation in 5 minutes!

## Prerequisites Check

- [ ] Python 3.8+ installed
- [ ] Autodesk Platform Services account
- [ ] OpenAI or Anthropic API key

## Installation

### 1. Clone/Download the Project

```bash
cd Hackathon
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env

# Edit .env with your credentials
```

Minimum required variables:
```env
APS_CLIENT_ID=your_client_id
APS_CLIENT_SECRET=your_client_secret
OPENAI_API_KEY=your_openai_key
```

### 4. Test the Setup

Run a dry-run demo:
```bash
python examples/demo.py \
  --project-id YOUR_PROJECT_ID \
  --design-id YOUR_DESIGN_ID \
  --intent "Minimize weight" \
  --dry-run
```

## Basic Usage

### Python Script

```python
from src.fusion360.client import Fusion360Client
from src.ai.optimizer import ParameterOptimizer

# Initialize
fusion_client = Fusion360Client()
ai_optimizer = ParameterOptimizer()

# Load model
model = fusion_client.load_model("project_id", "design_id")

# Get current parameters
params = model.get_parameters()

# Get AI suggestions
optimized = ai_optimizer.suggest_parameters(
    current_parameters=params,
    design_intent="Minimize weight while maintaining strength"
)

# Update and regenerate
model.update_parameters(optimized)
model.regenerate()
```

### Command Line

```bash
# Single model optimization
python examples/demo.py \
  --project-id <id> \
  --design-id <id> \
  --intent "Your design intent"

# Batch processing
python examples/batch_update.py --config config/batch_config.yaml
```

### Web UI (Future Scope)

```bash
python examples/web_ui_example.py
# Visit http://localhost:5000
```

## Common Issues

### "APS_CLIENT_ID not set"
- Make sure `.env` file exists and contains your credentials
- Check that variable names match exactly

### "Authentication failed"
- Verify your APS credentials are correct
- Check OAuth redirect URLs match your app settings

### "Model not found"
- Ensure project_id and design_id are correct
- Verify you have access to the project

### "AI API error"
- Check your API key is valid
- Verify you have API credits/quota available

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for detailed setup
- See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for API details
- Explore [examples/](examples/) for more use cases

## Getting Help

1. Check the documentation in `docs/`
2. Review example scripts in `examples/`
3. Check error messages for specific guidance

Happy designing! 🚀


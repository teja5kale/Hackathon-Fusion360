# AI-Assisted Parametric Design Automation

**Team: AI Catalysts**  
**Hackathon: Design & Make with AI**

## Problem Statement

Manual parametric updates in CAD models are repetitive and error-prone:
- Designers spend excessive time modifying dimensions
- Rapid design iteration becomes slow and inefficient
- High chance of human error during frequent changes

## Solution Overview

AI-assisted automation of parametric CAD models:
- Fusion 360 API updates parameters programmatically
- AI suggests optimized dimensions based on intent and constraints
- Enables rapid and repeatable design iteration

## Architecture

```
User Input / AI Prompt
    ↓
AI Logic (LLM or rule-based engine)
    ↓
Fusion 360 API (Python Automation)
    ↓
Automatic Parametric Model Regeneration
```

## Technology Stack

- **Autodesk Platform Services (APS)** - Fusion 360 API
- **Python** - Scripting and automation
- **AI/LLM** - Parameter optimization logic
- **OAuth 2.0** - Authentication

## Project Structure

```
.
├── src/
│   ├── auth/              # OAuth 2.0 authentication
│   ├── fusion360/         # Fusion 360 API client
│   ├── ai/                # AI parameter optimizer
│   └── models/            # Data models
├── examples/              # Demo scripts and examples
├── config/                # Configuration files
├── tests/                 # Unit tests
└── docs/                  # Documentation
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Set up Autodesk Platform Services:**
   - Create an app at https://aps.autodesk.com/
   - Get Client ID and Client Secret
   - Set up OAuth redirect URLs

4. **Configure AI provider:**
   - Add OpenAI, Anthropic, or Gemini API key to `.env`

## Usage

### Basic Example

```python
from src.fusion360.client import Fusion360Client
from src.ai.optimizer import ParameterOptimizer
from src.models.parameter import ParameterUpdate

# Initialize clients
fusion_client = Fusion360Client()
ai_optimizer = ParameterOptimizer()

# Load parametric model
model = fusion_client.load_model("project_id", "design_id")

# Get current parameters
current_params = model.get_parameters()

# AI suggests optimized values
design_intent = "Minimize weight while maintaining structural integrity"
optimized_params = ai_optimizer.suggest_parameters(
    current_params, 
    design_intent
)

# Update model
fusion_client.update_parameters(model.id, optimized_params)

# Regenerate geometry
fusion_client.regenerate_model(model.id)
```

### Command Line Interface

```bash
# Update parameters with AI suggestions
python examples/demo.py --model-id <model_id> --intent "Minimize weight"

# Batch update multiple models
python examples/batch_update.py --config config/batch_config.yaml
```

## Demo Flow

1. Load base parametric model
2. Provide design intent / constraints
3. AI suggests optimized parameters
4. Script updates model parameters
5. Fusion regenerates geometry instantly

## Business Value

- ✅ Faster design iterations
- ✅ Reduced manual effort and errors
- ✅ Improved designer productivity
- ✅ Scalable automation for engineering teams

## Future Scope

- Web-based UI for parameter inputs
- Simulation-driven AI optimization
- Integration with ACC and Forge Viewer
- Automated variant generation

## License

MIT License - Hackathon Project

## Team

**AI Catalysts**


# Project Structure

```
Hackathon/
│
├── src/                          # Main source code
│   ├── __init__.py
│   │
│   ├── auth/                    # OAuth 2.0 authentication
│   │   ├── __init__.py
│   │   └── oauth_client.py      # APS OAuth client
│   │
│   ├── fusion360/               # Fusion 360 API integration
│   │   ├── __init__.py
│   │   ├── client.py            # Fusion 360 API client
│   │   └── model.py             # ParametricModel class
│   │
│   ├── ai/                      # AI/LLM integration
│   │   ├── __init__.py
│   │   ├── optimizer.py         # ParameterOptimizer class
│   │   └── prompts.py           # Prompt templates
│   │
│   └── models/                  # Data models
│       ├── __init__.py
│       └── parameter.py         # Parameter data models
│
├── examples/                    # Example scripts and demos
│   ├── demo.py                  # Main demo script (CLI)
│   ├── simple_example.py        # Basic usage example
│   ├── batch_update.py          # Batch processing script
│   └── web_ui_example.py        # Web UI example (future scope)
│
├── config/                      # Configuration files
│   └── batch_config.example.yaml # Batch processing config template
│
├── tests/                       # Unit tests
│   ├── __init__.py
│   └── test_ai_optimizer.py    # AI optimizer tests
│
├── docs/                        # Documentation
│   ├── API_REFERENCE.md         # API documentation
│   └── SETUP_GUIDE.md           # Detailed setup guide
│
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── README.md                    # Main documentation
├── QUICKSTART.md               # Quick start guide
├── PROJECT_STRUCTURE.md        # This file
└── LICENSE                      # MIT License

```

## Key Components

### Authentication (`src/auth/`)
- **OAuthClient**: Handles OAuth 2.0 flow with Autodesk Platform Services
- Supports both authorization code and client credentials flows
- Automatic token refresh

### Fusion 360 Integration (`src/fusion360/`)
- **Fusion360Client**: Main API client for Fusion 360 operations
- **ParametricModel**: Represents a parametric CAD model
- Methods for loading, updating parameters, and regenerating models

### AI Optimization (`src/ai/`)
- **ParameterOptimizer**: Uses LLMs to suggest optimized parameters
- Supports OpenAI and Anthropic Claude
- **DesignIntentPrompt**: Creates prompts for AI optimization

### Data Models (`src/models/`)
- **ParameterUpdate**: Represents a parameter update
- **ParameterConstraint**: Defines constraints on parameters
- **ParameterSet**: Collection of parameter updates

### Examples (`examples/`)
- **demo.py**: Full-featured CLI demo
- **simple_example.py**: Minimal usage example
- **batch_update.py**: Process multiple models
- **web_ui_example.py**: Flask web interface (future scope)

## Data Flow

```
User Input (Design Intent)
    ↓
ParameterOptimizer.suggest_parameters()
    ↓
AI/LLM (OpenAI/Anthropic)
    ↓
Optimized Parameters
    ↓
Fusion360Client.update_parameters()
    ↓
Fusion 360 API
    ↓
Model Regeneration
```

## Extension Points

### Adding New AI Providers
1. Add provider SDK to `requirements.txt`
2. Extend `ParameterOptimizer` with new provider method
3. Update `_suggest_with_*` methods

### Adding New Fusion 360 Operations
1. Add method to `Fusion360Client`
2. Optionally add wrapper to `ParametricModel`
3. Update API reference docs

### Custom Constraints
1. Extend `ParameterConstraint` model
2. Update validation logic in `ParameterUpdate`
3. Modify prompt templates to include constraints


# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   CLI Demo   │  │  Web UI      │  │  Batch Proc  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         ParameterOptimizer (AI Logic)                │  │
│  │  - Design Intent Analysis                            │  │
│  │  - Parameter Suggestion                              │  │
│  │  - Explanation Generation                            │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Fusion360Client (CAD Integration)            │  │
│  │  - Model Loading                                     │  │
│  │  - Parameter Updates                                 │  │
│  │  - Model Regeneration                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌──────────────────────┐            ┌──────────────────────┐
│   AI Provider APIs   │            │  Autodesk Platform   │
│  ┌────────────────┐  │            │      Services        │
│  │   OpenAI API   │  │            │  ┌────────────────┐ │
│  └────────────────┘  │            │  │ Fusion 360 API │ │
│  ┌────────────────┐  │            │  └────────────────┘ │
│  │ Anthropic API  │  │            │  ┌────────────────┐ │
│  └────────────────┘  │            │  │  OAuth 2.0     │ │
└──────────────────────┘            │  └────────────────┘ │
                                   └──────────────────────┘
```

## Component Interactions

### 1. Authentication Flow

```
Application
    │
    ├─> OAuthClient.get_token_from_client_credentials()
    │       │
    │       └─> POST /authentication/v2/token
    │               │
    │               └─> APS Authentication Server
    │                       │
    │                       └─> Returns: access_token, expires_in
    │
    └─> Token stored with expiration tracking
```

### 2. Parameter Optimization Flow

```
User provides design intent
    │
    ├─> ParameterOptimizer.suggest_parameters()
    │       │
    │       ├─> DesignIntentPrompt.create()
    │       │       └─> Formats prompt with:
    │       │           - Current parameters
    │       │           - Design intent
    │       │           - Constraints
    │       │
    │       └─> AI Provider API Call
    │               │
    │               ├─> OpenAI: chat.completions.create()
    │               │       └─> Returns JSON with suggestions
    │               │
    │               └─> Anthropic: messages.create()
    │                       └─> Returns text (JSON extracted)
    │
    └─> Returns optimized parameters dictionary
```

### 3. Model Update Flow

```
Optimized parameters
    │
    ├─> Fusion360Client.update_parameters()
    │       │
    │       └─> PUT /fusion/v1/projects/{id}/designs/{id}/parameters
    │               │
    │               └─> APS Fusion 360 API
    │                       │
    │                       └─> Updates parametric model
    │
    └─> Fusion360Client.regenerate_model()
            │
            └─> POST /fusion/v1/projects/{id}/designs/{id}/regenerate
                    │
                    └─> APS Fusion 360 API
                            │
                            └─> Triggers geometry regeneration
```

## Data Models

### ParameterUpdate
```python
{
    "name": "length",
    "value": 100.0,
    "unit": "mm",
    "constraint": {
        "min_value": 50.0,
        "max_value": 200.0
    }
}
```

### Design Intent Input
```python
{
    "design_intent": "Minimize weight while maintaining strength",
    "constraints": {
        "max_stress": 100,  # MPa
        "min_volume": 50    # cm³
    }
}
```

## Security Considerations

1. **OAuth 2.0**: Secure token-based authentication
2. **Environment Variables**: Sensitive credentials stored in `.env`
3. **Token Refresh**: Automatic token refresh before expiration
4. **API Keys**: AI provider keys never exposed in code

## Error Handling

- **Authentication Errors**: Retry with token refresh
- **API Errors**: Graceful degradation with error messages
- **AI Errors**: Fallback to rule-based suggestions (future)
- **Validation**: Parameter constraints enforced before updates

## Scalability Considerations

1. **Batch Processing**: Process multiple models efficiently
2. **Async Operations**: Can be extended with async/await
3. **Caching**: Token caching reduces API calls
4. **Rate Limiting**: Respects API rate limits

## Future Enhancements

1. **Web UI**: Full-featured web interface
2. **Simulation Integration**: FEA/CFD-driven optimization
3. **ACC Integration**: Autodesk Construction Cloud
4. **Forge Viewer**: 3D model visualization
5. **Variant Generation**: Automated design variant creation


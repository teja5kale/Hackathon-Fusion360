# API Reference

## OAuthClient

Handles authentication with Autodesk Platform Services.

### Methods

#### `get_authorization_url() -> str`
Get the authorization URL for user authentication.

#### `get_token_from_code(authorization_code: str) -> Dict`
Exchange authorization code for access token.

#### `get_token_from_client_credentials() -> Dict`
Get access token using client credentials flow.

#### `get_access_token() -> str`
Get valid access token, refreshing if necessary.

## Fusion360Client

Client for interacting with Fusion 360 API.

### Methods

#### `load_model(project_id: str, design_id: str) -> ParametricModel`
Load a parametric model from Fusion 360.

#### `get_parameters(project_id: str, design_id: str) -> Dict[str, Any]`
Get all parameters from a parametric model.

#### `update_parameters(project_id: str, design_id: str, parameters: Dict[str, Any]) -> Dict`
Update parameters in a parametric model.

#### `regenerate_model(project_id: str, design_id: str) -> Dict`
Trigger model regeneration after parameter updates.

## ParameterOptimizer

AI-powered parameter optimization using LLMs.

### Methods

#### `suggest_parameters(current_parameters: Dict[str, Any], design_intent: str, constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
Suggest optimized parameter values based on design intent.

#### `explain_suggestions(current_parameters: Dict[str, Any], suggested_parameters: Dict[str, Any], design_intent: str) -> str`
Get explanation for parameter suggestions.

## ParametricModel

Represents a parametric Fusion 360 model.

### Methods

#### `get_parameters() -> Dict[str, Any]`
Get all parameters from this model.

#### `update_parameters(parameters: Dict[str, Any]) -> Dict`
Update parameters in this model.

#### `regenerate() -> Dict`
Regenerate model geometry after parameter updates.


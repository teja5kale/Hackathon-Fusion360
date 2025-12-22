"""
Prompt templates for AI parameter optimization
"""

from typing import Dict, Any


class DesignIntentPrompt:
    """Creates prompts for AI parameter optimization"""
    
    @staticmethod
    def create(current_parameters: Dict[str, Any],
               design_intent: str,
               constraints: Dict[str, Any] = None) -> str:
        """
        Create a prompt for parameter optimization
        
        Args:
            current_parameters: Current parameter values
            design_intent: Design goal description
            constraints: Design constraints
            
        Returns:
            Formatted prompt string
        """
        constraints = constraints or {}
        
        prompt = f"""You are a CAD parameter optimization expert. Analyze the current parametric model and suggest optimized parameter values based on the design intent.

DESIGN INTENT:
{design_intent}

CURRENT PARAMETERS:
"""
        for param_name, param_value in current_parameters.items():
            prompt += f"  - {param_name}: {param_value}\n"
        
        if constraints:
            prompt += "\nCONSTRAINTS:\n"
            for constraint_name, constraint_value in constraints.items():
                prompt += f"  - {constraint_name}: {constraint_value}\n"
        
        prompt += """
TASK:
Suggest optimized parameter values that align with the design intent while respecting any constraints. Consider:
- Engineering best practices
- Material properties
- Manufacturing constraints
- Performance optimization
- Safety factors

Return your response as a JSON object with this structure:
{
  "parameters": {
    "parameter_name_1": suggested_value_1,
    "parameter_name_2": suggested_value_2,
    ...
  },
  "reasoning": "Brief explanation of the changes"
}

Only suggest changes to parameters that would improve the design. Keep unchanged parameters at their current values.
"""
        return prompt


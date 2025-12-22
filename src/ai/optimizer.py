"""
AI Parameter Optimizer
Uses LLM to suggest optimized parameter values based on design intent
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from src.ai.prompts import DesignIntentPrompt

load_dotenv()


class ParameterOptimizer:
    """AI-powered parameter optimization using LLMs"""
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize AI optimizer
        
        Args:
            provider: AI provider ("openai", "anthropic", or "gemini")
            model: Model name (uses default if not provided)
        """
        self.provider = (provider or os.getenv("AI_PROVIDER", "openai")).lower()
        self.model = model or self._get_default_model()
        
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed")
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            self.client = openai.OpenAI(api_key=api_key)
            
        elif self.provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package not installed")
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            self.client = anthropic.Anthropic(api_key=api_key)
        
        elif self.provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("google-genai package not installed")
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set in environment")
            self.model = self._normalize_gemini_model(self.model)
            self.client = genai.Client(api_key=api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _get_default_model(self) -> str:
        """Get default model based on provider"""
        model = os.getenv("AI_MODEL")
        if model:
            return model
        
        if self.provider == "openai":
            return "gpt-3.5-turbo"  # Widely available model
        elif self.provider == "anthropic":
            return "claude-3-opus-20240229"
        elif self.provider == "gemini":
            # Default to a broadly available v1beta-supported model
            return "models/gemini-1.5-flash"
        return "gpt-3.5-turbo"
    
    def suggest_parameters(self, 
                          current_parameters: Dict[str, Any],
                          design_intent: str,
                          constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Suggest optimized parameter values based on design intent
        
        Args:
            current_parameters: Current parameter values
            design_intent: Description of design goals (e.g., "Minimize weight")
            constraints: Optional constraints (e.g., {"max_stress": 100, "min_volume": 50})
            
        Returns:
            Dictionary of suggested parameter values
        """
        prompt = DesignIntentPrompt.create(
            current_parameters=current_parameters,
            design_intent=design_intent,
            constraints=constraints or {}
        )
        
        if self.provider == "openai":
            return self._suggest_with_openai(prompt)
        elif self.provider == "anthropic":
            return self._suggest_with_anthropic(prompt)
        elif self.provider == "gemini":
            return self._suggest_with_gemini(prompt)
    
    def _suggest_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Get suggestions using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a CAD parameter optimization expert. Return only valid JSON with parameter names and suggested values."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("parameters", {})
    
    def _suggest_with_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Get suggestions using Anthropic Claude"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract JSON from response
        content = message.content[0].text
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result.get("parameters", {})
        else:
            raise ValueError("Could not parse JSON from AI response")

    def _suggest_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Get suggestions using Google Gemini"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                ),
            )
        except Exception as exc:
            # Provide a clearer hint when the model name is unsupported
            raise ValueError(
                f"Gemini model '{self.model}' not found or unsupported. "
                f"Set AI_MODEL to a supported model (e.g., gemini-1.5-flash) "
                f"or check your API version."
            ) from exc

        # Some Gemini responses may include reasoning; attempt to parse JSON
        text = self._extract_text_from_genai(response)
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError("Could not parse JSON from Gemini response")

        result = json.loads(json_match.group())
        return result.get("parameters", {})
    
    def explain_suggestions(self, 
                           current_parameters: Dict[str, Any],
                           suggested_parameters: Dict[str, Any],
                           design_intent: str) -> str:
        """
        Get explanation for parameter suggestions
        
        Args:
            current_parameters: Original parameter values
            suggested_parameters: AI-suggested parameter values
            design_intent: Design intent description
            
        Returns:
            Explanation string
        """
        explanation_prompt = f"""
Explain why these parameter changes were suggested for the design intent: "{design_intent}"

Current Parameters:
{self._format_parameters(current_parameters)}

Suggested Parameters:
{self._format_parameters(suggested_parameters)}

Provide a clear explanation of the reasoning behind each change.
"""
        
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": explanation_prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        elif self.provider == "anthropic":
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": explanation_prompt}]
            )
            return message.content[0].text
        elif self.provider == "gemini":
            response = self.client.models.generate_content(
                model=self.model,
                contents=explanation_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.7,
                ),
            )
            return self._extract_text_from_genai(response)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _format_parameters(self, parameters: Dict[str, Any]) -> str:
        """Format parameters dictionary for display"""
        return "\n".join([f"  {k}: {v}" for k, v in parameters.items()])

    def _extract_text_from_genai(self, response: Any) -> str:
        """Extract text content from genai response safely"""
        if hasattr(response, "text") and response.text:
            return response.text
        try:
            candidate = response.candidates[0]
            parts = getattr(candidate, "content", candidate).parts
            texts = [getattr(p, "text", "") for p in parts if getattr(p, "text", "")]
            return "\n".join(texts)
        except Exception:
            return ""

    def _normalize_gemini_model(self, model_name: str) -> str:
        """Ensure Gemini model name includes the required 'models/' prefix"""
        if not model_name:
            return "models/gemini-1.5-flash"
        if model_name.startswith("models/"):
            return model_name
        return f"models/{model_name}"


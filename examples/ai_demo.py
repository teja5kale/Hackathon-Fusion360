"""
Standalone AI Demo - Shows AI parameter optimization without Fusion 360 API
This demo works without APS credentials, showing only the AI optimization capabilities
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.optimizer import ParameterOptimizer
from src.ai.prompts import DesignIntentPrompt


def demo_ai_optimization():
    """Demonstrate AI parameter optimization with mock data"""
    
    print("=" * 70)
    print("AI-Assisted Parametric Design Automation - AI Demo")
    print("Team: AI Catalysts")
    print("=" * 70)
    print()
    
    # Mock parametric model parameters
    current_parameters = {
        "length": 100.0,      # mm
        "width": 50.0,        # mm
        "height": 25.0,       # mm
        "thickness": 5.0,     # mm
        "wall_thickness": 3.0, # mm
        "corner_radius": 2.0  # mm
    }
    
    design_intent = "Minimize weight while maintaining structural integrity and keeping dimensions within manufacturing constraints"
    
    constraints = {
        "min_length": 80.0,
        "max_length": 120.0,
        "min_thickness": 3.0,
        "max_stress": 100  # MPa
    }
    
    print("Current Parametric Model Parameters:")
    print("-" * 70)
    for param_name, param_value in current_parameters.items():
        print(f"  {param_name:20s}: {param_value:8.2f}")
    print()
    
    print(f"Design Intent: {design_intent}")
    print()
    
    print("Constraints:")
    print("-" * 70)
    for constraint_name, constraint_value in constraints.items():
        print(f"  {constraint_name:20s}: {constraint_value}")
    print()
    
    # Decide provider based on env
    preferred_provider = os.getenv("AI_PROVIDER", "").lower()
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    provider = preferred_provider or ("gemini" if has_gemini else "openai")

    # Check API key availability
    if provider == "openai" and not has_openai:
        provider = "gemini" if has_gemini else provider
    if provider == "anthropic" and not has_anthropic:
        provider = "gemini" if has_gemini else provider
    if provider == "gemini" and not has_gemini:
        provider = "openai" if has_openai else provider

    key_present = (
        (provider == "openai" and has_openai) or
        (provider == "anthropic" and has_anthropic) or
        (provider == "gemini" and has_gemini)
    )

    if not key_present:
        print("[!] No AI API key configured.")
        print("    Set one of OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY/GOOGLE_API_KEY in your .env file.")
        print()
        print("For now, showing the prompt that would be sent to AI:")
        print("=" * 70)
        prompt = DesignIntentPrompt.create(
            current_parameters=current_parameters,
            design_intent=design_intent,
            constraints=constraints
        )
        print(prompt)
        print("=" * 70)
        return
    
    # Initialize AI optimizer
    print(f"Initializing AI optimizer (provider: {provider})...")
    try:
        optimizer = ParameterOptimizer(provider=provider)
        print("[OK] AI optimizer initialized")
        print()
        
        # Get AI suggestions
        print("AI analyzing design intent and suggesting optimizations...")
        print("-" * 70)
        
        optimized_params = optimizer.suggest_parameters(
            current_parameters=current_parameters,
            design_intent=design_intent,
            constraints=constraints
        )
        
        print("\n[OK] AI Suggestions Received:")
        print("=" * 70)
        print(f"{'Parameter':<20s} {'Current':>12s} {'Suggested':>12s} {'Change':>12s}")
        print("-" * 70)
        
        for param_name in current_parameters.keys():
            current_val = current_parameters.get(param_name, 0)
            suggested_val = optimized_params.get(param_name, current_val)
            change = suggested_val - current_val
            change_pct = (change / current_val * 100) if current_val != 0 else 0
            
            change_str = f"{change:+.2f} ({change_pct:+.1f}%)"
            print(f"{param_name:<20s} {current_val:>12.2f} {suggested_val:>12.2f} {change_str:>12s}")
        
        print("=" * 70)
        print()
        
        # Get explanation
        print("Getting AI explanation...")
        print("-" * 70)
        explanation = optimizer.explain_suggestions(
            current_parameters=current_parameters,
            suggested_parameters=optimized_params,
            design_intent=design_intent
        )
        print(explanation)
        print()
        
        print("=" * 70)
        print("[OK] Demo completed successfully!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Set up Autodesk Platform Services credentials")
        print("  2. Use Fusion360Client to load and update actual models")
        print("  3. Run: python examples/demo.py --project-id <id> --design-id <id> --intent 'Your intent'")
        
    except Exception as e:
        print(f"[X] Error: {e}")
        print()
        print("This might be due to:")
        print("  - Invalid OpenAI API key")
        print("  - Network connectivity issues")
        print("  - API quota exceeded")
        print()
        print("Showing prompt that would be sent:")
        print("=" * 70)
        prompt = DesignIntentPrompt.create(
            current_parameters=current_parameters,
            design_intent=design_intent,
            constraints=constraints
        )
        print(prompt)


if __name__ == "__main__":
    demo_ai_optimization()


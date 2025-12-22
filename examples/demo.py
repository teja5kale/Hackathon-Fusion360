"""
Demo script for AI-Assisted Parametric Design Automation
Demonstrates the complete workflow: Load → Optimize → Update → Regenerate
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fusion360.client import Fusion360Client
from src.ai.optimizer import ParameterOptimizer
from src.models.parameter import ParameterSet


def main():
    parser = argparse.ArgumentParser(
        description="AI-Assisted Parametric Design Automation Demo"
    )
    parser.add_argument(
        "--project-id",
        required=True,
        help="Fusion 360 Project ID"
    )
    parser.add_argument(
        "--design-id",
        required=True,
        help="Fusion 360 Design ID"
    )
    parser.add_argument(
        "--intent",
        required=True,
        help="Design intent (e.g., 'Minimize weight while maintaining strength')"
    )
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "openai", "anthropic", "gemini"],
        help="AI provider to use (auto picks based on available keys)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show suggestions without updating the model"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("AI-Assisted Parametric Design Automation")
    print("Team: AI Catalysts")
    print("=" * 60)
    print()
    
    # Resolve provider
    env_provider = os.getenv("AI_PROVIDER", "").lower()
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    provider = env_provider or args.provider
    if provider == "auto" or provider == "":
        provider = "gemini" if has_gemini else ("openai" if has_openai else "anthropic")

    # Fallbacks if selected provider lacks key
    if provider == "openai" and not has_openai:
        provider = "gemini" if has_gemini else provider
    if provider == "anthropic" and not has_anthropic:
        provider = "gemini" if has_gemini else provider
    if provider == "gemini" and not has_gemini:
        provider = "openai" if has_openai else provider

    # Initialize clients
    print("1. Initializing clients...")
    try:
        fusion_client = Fusion360Client()
        ai_optimizer = ParameterOptimizer(provider=provider)
        print(f"   [OK] Clients initialized (provider: {provider})")
    except Exception as e:
        print(f"   [X] Error initializing clients: {e}")
        return 1
    
    # Load model
    print(f"\n2. Loading parametric model...")
    print(f"   Project ID: {args.project_id}")
    print(f"   Design ID: {args.design_id}")
    try:
        model = fusion_client.load_model(args.project_id, args.design_id)
        print(f"   [OK] Model loaded: {model.name}")
    except Exception as e:
        error_msg = str(e)
        print(f"   [!] Could not load model from Fusion 360 API: {error_msg}")
        print(f"   Note: Fusion 360 cloud API may require beta access")
        print(f"   Continuing with mock parameters to demonstrate AI optimization...")
        print()
        
        # Create a mock model for demo purposes
        from src.fusion360.model import ParametricModel
        model = ParametricModel(
            client=fusion_client,
            project_id=args.project_id,
            design_id=args.design_id,
            data={'attributes': {'displayName': 'Demo Model (Mock)'}}
        )
    
    # Get current parameters
    print(f"\n3. Retrieving current parameters...")
    try:
        current_params = model.get_parameters()
        print(f"   [OK] Found {len(current_params)} parameters:")
        for name, value in current_params.items():
            print(f"     - {name}: {value}")
    except Exception as e:
        print(f"   [X] Error retrieving parameters: {e}")
        print("   Note: Using mock parameters for demo")
        current_params = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0,
            "thickness": 5.0
        }
        print(f"   Mock parameters:")
        for name, value in current_params.items():
            print(f"     - {name}: {value}")
    
    # AI suggests optimized parameters
    print(f"\n4. AI analyzing design intent and suggesting optimizations...")
    print(f"   Design Intent: {args.intent}")
    try:
        optimized_params = ai_optimizer.suggest_parameters(
            current_parameters=current_params,
            design_intent=args.intent
        )
        print(f"   [OK] AI suggestions received:")
        for name, value in optimized_params.items():
            old_value = current_params.get(name, "N/A")
            change = ""
            if name in current_params:
                change_pct = ((value - old_value) / old_value * 100) if old_value != 0 else 0
                change = f" ({change_pct:+.1f}%)"
            print(f"     - {name}: {old_value} → {value}{change}")
    except Exception as e:
        print(f"   [X] Error getting AI suggestions: {e}")
        return 1
    
    # Get explanation
    print(f"\n5. Getting AI explanation...")
    try:
        explanation = ai_optimizer.explain_suggestions(
            current_parameters=current_params,
            suggested_parameters=optimized_params,
            design_intent=args.intent
        )
        print(f"   [OK] Explanation:")
        print(f"   {explanation}")
    except Exception as e:
        print(f"   [!] Could not get explanation: {e}")
    
    # Update model (if not dry run)
    if not args.dry_run:
        print(f"\n6. Updating model parameters...")
        try:
            update_response = model.update_parameters(optimized_params)
            print(f"   [OK] Parameters updated successfully")
        except Exception as e:
            print(f"   [X] Error updating parameters: {e}")
            print("   Note: This may be due to API endpoint differences")
            return 1
        
        # Regenerate model
        print(f"\n7. Regenerating model geometry...")
        try:
            regenerate_response = model.regenerate()
            print(f"   [OK] Model regenerated successfully")
        except Exception as e:
            print(f"   [X] Error regenerating model: {e}")
            print("   Note: This may be due to API endpoint differences")
    else:
        print(f"\n6. Dry run mode - skipping parameter update")
        print(f"   Remove --dry-run flag to apply changes")
    
    print(f"\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


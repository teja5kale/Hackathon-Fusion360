"""
Simple example demonstrating basic usage
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fusion360.client import Fusion360Client
from src.ai.optimizer import ParameterOptimizer


def simple_example():
    """Simple example workflow"""
    
    # Initialize clients
    print("Initializing...")
    try:
        fusion_client = Fusion360Client()
        print("[OK] Fusion360Client initialized")
    except Exception as e:
        print(f"[!] Fusion360Client initialization failed: {e}")
        print("   (This is expected if APS credentials are not configured)")
        fusion_client = None
    
    try:
        ai_optimizer = ParameterOptimizer()
        print("[OK] ParameterOptimizer initialized")
    except Exception as e:
        print(f"[!] ParameterOptimizer initialization failed: {e}")
        print("   (This is expected if OpenAI API key is not configured)")
        ai_optimizer = None
    
    if not fusion_client or not ai_optimizer:
        print("\n" + "=" * 60)
        print("Setup Required:")
        print("=" * 60)
        print("To run the full example, you need:")
        print("1. APS_CLIENT_ID and APS_CLIENT_SECRET in .env")
        print("2. OPENAI_API_KEY in .env (or ANTHROPIC_API_KEY)")
        print("3. Valid project_id and design_id")
        print("\nFor now, run: python examples/ai_demo.py")
        print("   to see the AI optimization demo without Fusion 360 API")
        return
    
    # Example: Load a model (replace with your IDs)
    project_id = "your_project_id"
    design_id = "your_design_id"
    
    try:
        # Load model
        model = fusion_client.load_model(project_id, design_id)
        print(f"Loaded model: {model.name}")
        
        # Get current parameters
        current_params = model.get_parameters()
        print(f"Current parameters: {current_params}")
        
        # Get AI suggestions
        design_intent = "Minimize weight while maintaining strength"
        optimized_params = ai_optimizer.suggest_parameters(
            current_parameters=current_params,
            design_intent=design_intent
        )
        print(f"AI suggestions: {optimized_params}")
        
        # Update model
        model.update_parameters(optimized_params)
        model.regenerate()
        print("Model updated and regenerated!")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: Make sure to:")
        print("1. Set up your .env file with credentials")
        print("2. Use valid project_id and design_id")
        print("3. Have a parametric model in Fusion 360")


if __name__ == "__main__":
    simple_example()


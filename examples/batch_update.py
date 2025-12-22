"""
Batch update script for multiple models
Processes multiple designs with AI optimization
"""

import sys
import yaml
import json
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fusion360.client import Fusion360Client
from src.ai.optimizer import ParameterOptimizer


def load_batch_config(config_path: str) -> Dict:
    """Load batch configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def process_batch(config: Dict):
    """Process batch of models"""
    fusion_client = Fusion360Client()
    ai_optimizer = ParameterOptimizer(provider=config.get('ai_provider', 'openai'))
    
    results = []
    
    for item in config.get('items', []):
        project_id = item['project_id']
        design_id = item['design_id']
        design_intent = item['design_intent']
        constraints = item.get('constraints', {})
        
        print(f"\nProcessing: {design_id}")
        print(f"Intent: {design_intent}")
        
        try:
            # Load model
            model = fusion_client.load_model(project_id, design_id)
            
            # Get parameters
            current_params = model.get_parameters()
            
            # Get AI suggestions
            optimized_params = ai_optimizer.suggest_parameters(
                current_parameters=current_params,
                design_intent=design_intent,
                constraints=constraints
            )
            
            # Update model
            model.update_parameters(optimized_params)
            model.regenerate()
            
            results.append({
                'design_id': design_id,
                'status': 'success',
                'parameters': optimized_params
            })
            
            print(f"✓ Successfully updated {design_id}")
            
        except Exception as e:
            results.append({
                'design_id': design_id,
                'status': 'error',
                'error': str(e)
            })
            print(f"✗ Error processing {design_id}: {e}")
    
    # Save results
    output_path = config.get('output_file', 'batch_results.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBatch processing complete. Results saved to {output_path}")
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch update multiple models")
    parser.add_argument("--config", required=True, help="Path to batch config YAML")
    
    args = parser.parse_args()
    
    config = load_batch_config(args.config)
    process_batch(config)


"""
Standalone Fusion 360 Script: Apply AI Parameters
This script can be run directly in Fusion 360 without installing as an add-in
"""

import adsk.core
import adsk.fusion
import traceback
import json
import os
import sys

# Configuration
DESIGN_INTENT = "Minimize weight while maintaining structural integrity"
AI_PROVIDER = "openai"  # or "anthropic"
USE_JSON_FILE = False  # Set to True to load from JSON file
JSON_FILE_PATH = r"C:\Users\YourName\ai_parameters.json"  # Update this path


def get_current_parameters(design: adsk.fusion.Design) -> dict:
    """Get current user parameters from the design"""
    params = {}
    
    try:
        userParams = design.userParameters
        for param in userParams:
            value = param.value
            if hasattr(value, 'value'):
                value = value.value
            
            params[param.name] = {
                'value': value,
                'unit': param.unit if hasattr(param, 'unit') else '',
                'expression': param.expression if hasattr(param, 'expression') else str(value)
            }
    except Exception as e:
        print(f'Error reading parameters: {str(e)}')
    
    return params


def apply_parameters(design: adsk.fusion.Design, optimizedParams: dict) -> int:
    """Apply optimized parameters to the design"""
    applied_count = 0
    
    try:
        userParams = design.userParameters
        
        for paramName, paramValue in optimizedParams.items():
            # Find the parameter
            param = userParams.itemByName(paramName)
            
            if param:
                # Get the value
                if isinstance(paramValue, dict):
                    value = paramValue.get('value', paramValue)
                else:
                    value = paramValue
                
                # Update parameter expression
                try:
                    param.expression = str(value)
                    applied_count += 1
                    print(f'Updated {paramName}: {value}')
                except Exception as e:
                    print(f'Failed to update parameter {paramName}: {str(e)}')
            else:
                # Parameter doesn't exist, create it
                try:
                    if isinstance(paramValue, dict):
                        value = paramValue.get('value', paramValue)
                        unit = paramValue.get('unit', '')
                    else:
                        value = paramValue
                        unit = ''
                    
                    userParams.add(paramName, adsk.core.ValueInput.createByReal(float(value)), unit, '')
                    applied_count += 1
                    print(f'Created {paramName}: {value}')
                except Exception as e:
                    print(f'Failed to create parameter {paramName}: {str(e)}')
        
        # Regenerate the design
        design.regenerate()
        print('Design regenerated successfully!')
        
    except Exception as e:
        print(f'Error applying parameters: {str(e)}')
    
    return applied_count


def load_parameters_from_json(jsonFilePath: str) -> dict:
    """Load optimized parameters from a JSON file"""
    try:
        with open(jsonFilePath, 'r') as f:
            data = json.load(f)
            
        if 'parameters' in data:
            return data['parameters']
        elif isinstance(data, dict):
            return data
        else:
            return {}
    except Exception as e:
        print(f'Error loading JSON file: {str(e)}')
        return {}


def main():
    """Main function"""
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Get active design
        design = app.activeProduct
        
        if not design:
            ui.messageBox('No active design. Please open a design first.')
            return
        
        # Get current parameters
        currentParams = get_current_parameters(design)
        
        if not currentParams:
            ui.messageBox('No user parameters found in the design.')
            return
        
        print(f'Found {len(currentParams)} parameters:')
        for name, info in currentParams.items():
            print(f'  {name}: {info["value"]} {info.get("unit", "")}')
        
        # Get optimized parameters
        if USE_JSON_FILE and os.path.exists(JSON_FILE_PATH):
            # Load from JSON file
            print(f'\nLoading parameters from: {JSON_FILE_PATH}')
            optimizedParams = load_parameters_from_json(JSON_FILE_PATH)
        else:
            # Use AI optimization
            print(f'\nGetting AI suggestions...')
            print(f'Design Intent: {DESIGN_INTENT}')
            print(f'AI Provider: {AI_PROVIDER}')
            
            # Add project root to path
            # Update this path to your project directory
            project_root = r"D:\Hackathon"  # UPDATE THIS PATH
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            try:
                from src.ai.optimizer import ParameterOptimizer
                
                optimizer = ParameterOptimizer(provider=AI_PROVIDER)
                optimizedParams = optimizer.suggest_parameters(
                    current_parameters={k: v['value'] for k, v in currentParams.items()},
                    design_intent=DESIGN_INTENT
                )
                
                print('\nAI Suggestions:')
                for name, value in optimizedParams.items():
                    currentValue = currentParams.get(name, {}).get('value', 'N/A')
                    print(f'  {name}: {currentValue} → {value}')
                
            except ImportError:
                ui.messageBox('AI optimizer not available. Please ensure the project is accessible.')
                return
            except Exception as e:
                ui.messageBox(f'AI optimization failed: {str(e)}')
                return
        
        # Apply parameters
        print('\nApplying parameters...')
        applied_count = apply_parameters(design, optimizedParams)
        
        # Show results
        if applied_count > 0:
            ui.messageBox(f'Successfully applied {applied_count} parameter(s)!')
        else:
            ui.messageBox('No parameters were updated.')
            
    except:
        ui = adsk.core.Application.get().userInterface
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Run the script
if __name__ == '__main__':
    main()


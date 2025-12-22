"""
Fusion 360 Add-in: Apply AI-Optimized Parameters
Command to apply AI-suggested parameter values to the active design
"""

import adsk.core
import adsk.fusion
import traceback
import json
import os
import sys

# Add parent directory to path to import our AI optimizer
# Adjust this path based on where your project is located
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.ai.optimizer import ParameterOptimizer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


# Global variables
_app = None
_ui = None
_handlers = []


def run(context):
    """Entry point for the add-in command"""
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        # Create command definition
        cmdDef = _ui.commandDefinitions.addButtonDefinition(
            'aiApplyParams',
            'Apply AI Parameters',
            'Apply AI-optimized parameter values to the active design',
            ''
        )
        
        # Connect to command created event
        onCommandCreated = ApplyAIParametersCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        # Add to toolbar (you can customize this)
        designWorkspace = _ui.workspaces.itemById('FusionSolidEnvironment')
        if designWorkspace:
            toolbarPanel = designWorkspace.toolbarPanels.itemById('SolidModifyPanel')
            if toolbarPanel:
                toolbarPanel.controls.addCommand(cmdDef)
        
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    """Cleanup when add-in stops"""
    try:
        global _ui
        if _ui:
            _ui.messageBox('AI Parameter Optimizer add-in stopped')
    except:
        pass


class ApplyAIParametersCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Handler for when the command is created"""
    
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = ApplyAIParametersCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
            
            # Create input for design intent
            designIntentInput = cmd.commandInputs.addStringValueInput(
                'designIntent',
                'Design Intent',
                'e.g., Minimize weight while maintaining strength'
            )
            designIntentInput.tooltip = 'Describe your design optimization goal'
            
            # Create input for AI provider
            providerInput = cmd.commandInputs.addDropDownCommandInput(
                'aiProvider',
                'AI Provider',
                adsk.core.DropDownStyles.TextListDropDownStyle
            )
            providerInput.listItems.add('OpenAI', True)
            providerInput.listItems.add('Anthropic', False)
            
            # Create input for JSON file (optional)
            jsonFileInput = cmd.commandInputs.addStringValueInput(
                'jsonFile',
                'JSON File (Optional)',
                ''
            )
            jsonFileInput.tooltip = 'Path to JSON file with optimized parameters (leave empty to use AI)'
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ApplyAIParametersCommandExecuteHandler(adsk.core.CommandEventHandler):
    """Handler for when the command is executed"""
    
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            design = app.activeProduct
            
            if not design:
                _ui.messageBox('No active design. Please open a design first.')
                return
            
            # Get inputs
            inputs = args.command.commandInputs
            designIntent = inputs.itemById('designIntent').value
            providerIndex = inputs.itemById('aiProvider').selectedItem.index
            jsonFilePath = inputs.itemById('jsonFile').value
            
            provider = 'openai' if providerIndex == 0 else 'anthropic'
            
            # Get current parameters
            currentParams = get_current_parameters(design)
            
            if not currentParams:
                _ui.messageBox('No user parameters found in the design.')
                return
            
            # Get optimized parameters
            if jsonFilePath and os.path.exists(jsonFilePath):
                # Load from JSON file
                optimizedParams = load_parameters_from_json(jsonFilePath)
            elif AI_AVAILABLE and designIntent:
                # Use AI to optimize
                try:
                    optimizer = ParameterOptimizer(provider=provider)
                    optimizedParams = optimizer.suggest_parameters(
                        current_parameters=currentParams,
                        design_intent=designIntent
                    )
                except Exception as e:
                    _ui.messageBox(f'AI optimization failed: {str(e)}\n\nUsing current parameters.')
                    optimizedParams = currentParams
            else:
                _ui.messageBox('Please provide design intent or a JSON file with parameters.')
                return
            
            # Apply parameters
            applied_count = apply_parameters(design, optimizedParams, currentParams)
            
            # Show results
            if applied_count > 0:
                _ui.messageBox(f'Successfully applied {applied_count} parameter(s)!')
            else:
                _ui.messageBox('No parameters were updated.')
                
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def get_current_parameters(design: adsk.fusion.Design) -> dict:
    """
    Get current user parameters from the design
    
    Args:
        design: Fusion 360 Design object
        
    Returns:
        Dictionary of parameter names to values
    """
    params = {}
    
    try:
        userParams = design.userParameters
        for param in userParams:
            # Get parameter value (handle different unit types)
            value = param.value
            if hasattr(value, 'value'):
                value = value.value
            
            params[param.name] = {
                'value': value,
                'unit': param.unit if hasattr(param, 'unit') else '',
                'expression': param.expression if hasattr(param, 'expression') else str(value)
            }
    except Exception as e:
        _ui.messageBox(f'Error reading parameters: {str(e)}')
    
    return params


def apply_parameters(design: adsk.fusion.Design, optimizedParams: dict, currentParams: dict) -> int:
    """
    Apply optimized parameters to the design
    
    Args:
        design: Fusion 360 Design object
        optimizedParams: Dictionary of optimized parameter values
        currentParams: Dictionary of current parameter values
        
    Returns:
        Number of parameters successfully applied
    """
    applied_count = 0
    
    try:
        userParams = design.userParameters
        
        for paramName, paramValue in optimizedParams.items():
            # Find the parameter
            param = userParams.itemByName(paramName)
            
            if param:
                # Get the value (handle if it's a dict with 'value' key)
                if isinstance(paramValue, dict):
                    value = paramValue.get('value', paramValue)
                else:
                    value = paramValue
                
                # Update parameter expression
                # Fusion 360 uses expressions, so convert value to expression string
                try:
                    param.expression = str(value)
                    applied_count += 1
                except Exception as e:
                    _ui.messageBox(f'Failed to update parameter {paramName}: {str(e)}')
            else:
                # Parameter doesn't exist, create it
                try:
                    # Get unit from current params if available
                    unit = ''
                    if paramName in currentParams:
                        unit = currentParams[paramName].get('unit', '')
                    
                    # Create new parameter
                    if isinstance(paramValue, dict):
                        value = paramValue.get('value', paramValue)
                        unit = paramValue.get('unit', unit)
                    else:
                        value = paramValue
                    
                    userParams.add(paramName, adsk.core.ValueInput.createByReal(float(value)), unit, '')
                    applied_count += 1
                except Exception as e:
                    _ui.messageBox(f'Failed to create parameter {paramName}: {str(e)}')
        
        # Regenerate the design
        design.regenerate()
        
    except Exception as e:
        _ui.messageBox(f'Error applying parameters: {str(e)}')
    
    return applied_count


def load_parameters_from_json(jsonFilePath: str) -> dict:
    """
    Load optimized parameters from a JSON file
    
    Args:
        jsonFilePath: Path to JSON file
        
    Returns:
        Dictionary of parameters
    """
    try:
        with open(jsonFilePath, 'r') as f:
            data = json.load(f)
            
        # Handle different JSON structures
        if 'parameters' in data:
            return data['parameters']
        elif isinstance(data, dict):
            return data
        else:
            return {}
    except Exception as e:
        _ui.messageBox(f'Error loading JSON file: {str(e)}')
        return {}


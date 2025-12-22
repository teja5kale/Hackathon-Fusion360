"""
Fusion 360 Add-in: Get AI Suggestions
Command to get AI suggestions for current design parameters
"""

import adsk.core
import adsk.fusion
import traceback
import json
import os
import sys

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.ai.optimizer import ParameterOptimizer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


_app = None
_ui = None
_handlers = []


def run(context):
    """Entry point for the add-in command"""
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        cmdDef = _ui.commandDefinitions.addButtonDefinition(
            'aiGetSuggestions',
            'Get AI Suggestions',
            'Get AI-optimized parameter suggestions for the current design',
            ''
        )
        
        onCommandCreated = GetAISuggestionsCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        # Add to toolbar
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
        pass
    except:
        pass


class GetAISuggestionsCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Handler for when the command is created"""
    
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = GetAISuggestionsCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
            
            # Design intent input
            designIntentInput = cmd.commandInputs.addTextBoxCommandInput(
                'designIntent',
                'Design Intent',
                'Describe your design optimization goal:\n\nExample: Minimize weight while maintaining structural integrity',
                3,
                True
            )
            
            # AI provider
            providerInput = cmd.commandInputs.addDropDownCommandInput(
                'aiProvider',
                'AI Provider',
                adsk.core.DropDownStyles.TextListDropDownStyle
            )
            providerInput.listItems.add('OpenAI', True)
            providerInput.listItems.add('Anthropic', False)
            
            # Save to file option
            saveFileInput = cmd.commandInputs.addBoolValueInput(
                'saveToFile',
                'Save to JSON File',
                True,
                '',
                False
            )
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class GetAISuggestionsCommandExecuteHandler(adsk.core.CommandEventHandler):
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
            
            if not AI_AVAILABLE:
                _ui.messageBox('AI optimizer not available. Please ensure the project dependencies are installed.')
                return
            
            # Get inputs
            inputs = args.command.commandInputs
            designIntent = inputs.itemById('designIntent').value
            providerIndex = inputs.itemById('aiProvider').selectedItem.index
            saveToFile = inputs.itemById('saveToFile').value
            
            provider = 'openai' if providerIndex == 0 else 'anthropic'
            
            if not designIntent:
                _ui.messageBox('Please provide design intent.')
                return
            
            # Get current parameters
            currentParams = get_current_parameters(design)
            
            if not currentParams:
                _ui.messageBox('No user parameters found in the design.')
                return
            
            # Show progress
            _ui.messageBox('Getting AI suggestions... This may take a moment.')
            
            # Get AI suggestions
            try:
                optimizer = ParameterOptimizer(provider=provider)
                optimizedParams = optimizer.suggest_parameters(
                    current_parameters={k: v['value'] for k, v in currentParams.items()},
                    design_intent=designIntent
                )
                
                # Get explanation
                explanation = optimizer.explain_suggestions(
                    current_parameters={k: v['value'] for k, v in currentParams.items()},
                    suggested_parameters=optimizedParams,
                    design_intent=designIntent
                )
                
                # Display results
                result_text = "AI Parameter Suggestions:\n\n"
                result_text += "Current → Suggested:\n"
                result_text += "-" * 40 + "\n"
                
                for paramName, suggestedValue in optimizedParams.items():
                    currentValue = currentParams.get(paramName, {}).get('value', 'N/A')
                    change = ""
                    if isinstance(currentValue, (int, float)) and isinstance(suggestedValue, (int, float)):
                        if currentValue != 0:
                            change_pct = ((suggestedValue - currentValue) / currentValue * 100)
                            change = f" ({change_pct:+.1f}%)"
                    
                    result_text += f"{paramName}: {currentValue} → {suggestedValue}{change}\n"
                
                result_text += "\n" + "-" * 40 + "\n"
                result_text += "Explanation:\n"
                result_text += explanation[:500]  # Limit length
                
                _ui.messageBox(result_text)
                
                # Save to file if requested
                if saveToFile:
                    save_path = os.path.join(os.path.expanduser('~'), 'ai_parameters.json')
                    save_data = {
                        'parameters': optimizedParams,
                        'explanation': explanation,
                        'design_intent': designIntent
                    }
                    
                    with open(save_path, 'w') as f:
                        json.dump(save_data, f, indent=2)
                    
                    _ui.messageBox(f'Parameters saved to: {save_path}')
                
            except Exception as e:
                _ui.messageBox(f'AI optimization failed: {str(e)}\n\n{traceback.format_exc()}')
                
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


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
        _ui.messageBox(f'Error reading parameters: {str(e)}')
    
    return params


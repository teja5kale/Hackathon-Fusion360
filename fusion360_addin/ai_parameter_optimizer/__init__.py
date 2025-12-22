"""
AI Parameter Optimizer Fusion 360 Add-in
Main entry point
"""

import adsk.core

def run(context):
    """Run the add-in"""
    try:
        # Import and run commands
        from .commands import ApplyAIParameters, GetAISuggestions
        
        ApplyAIParameters.run(context)
        GetAISuggestions.run(context)
        
    except:
        ui = adsk.core.Application.get().userInterface
        ui.messageBox('Failed to initialize AI Parameter Optimizer add-in')


def stop(context):
    """Stop the add-in"""
    try:
        from .commands import ApplyAIParameters, GetAISuggestions
        
        ApplyAIParameters.stop(context)
        GetAISuggestions.stop(context)
    except:
        pass


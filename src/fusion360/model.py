"""
Parametric Model representation
"""

from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.fusion360.client import Fusion360Client


class ParametricModel:
    """Represents a parametric Fusion 360 model"""
    
    def __init__(self, client: "Fusion360Client", project_id: str, 
                 design_id: str, data: Dict[str, Any]):
        """
        Initialize parametric model
        
        Args:
            client: Fusion360Client instance
            project_id: Project ID
            design_id: Design ID
            data: Model data dictionary
        """
        self.client = client
        self.project_id = project_id
        self.design_id = design_id
        self.data = data
        self.id = design_id
        self.name = data.get('attributes', {}).get('displayName', 'Unnamed Model')
        
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get all parameters from this model
        
        Returns:
            Dictionary of parameter names to values
        """
        return self.client.get_parameters(self.project_id, self.design_id)
    
    def update_parameters(self, parameters: Dict[str, Any]) -> Dict:
        """
        Update parameters in this model
        
        Args:
            parameters: Dictionary of parameter names to new values
            
        Returns:
            Update response
        """
        return self.client.update_parameters(
            self.project_id, 
            self.design_id, 
            parameters
        )
    
    def regenerate(self) -> Dict:
        """
        Regenerate model geometry after parameter updates
        
        Returns:
            Regeneration response
        """
        return self.client.regenerate_model(self.project_id, self.design_id)
    
    def get_geometry(self) -> bytes:
        """
        Download model geometry
        
        Returns:
            Binary geometry data
        """
        return self.client.get_model_geometry(self.project_id, self.design_id)
    
    def __repr__(self) -> str:
        return f"ParametricModel(id={self.design_id}, name={self.name})"


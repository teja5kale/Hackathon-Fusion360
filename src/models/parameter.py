"""
Data models for parameter updates
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ParameterConstraint(BaseModel):
    """Represents a constraint on parameter values"""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[list] = None
    unit: Optional[str] = None


class ParameterUpdate(BaseModel):
    """Represents a parameter update request"""
    name: str = Field(..., description="Parameter name")
    value: Any = Field(..., description="New parameter value")
    unit: Optional[str] = Field(None, description="Parameter unit")
    constraint: Optional[ParameterConstraint] = Field(None, description="Parameter constraints")
    
    def validate(self) -> bool:
        """Validate parameter value against constraints"""
        if not self.constraint:
            return True
        
        if self.constraint.min_value is not None:
            if float(self.value) < self.constraint.min_value:
                return False
        
        if self.constraint.max_value is not None:
            if float(self.value) > self.constraint.max_value:
                return False
        
        if self.constraint.allowed_values is not None:
            if self.value not in self.constraint.allowed_values:
                return False
        
        return True


class ParameterSet(BaseModel):
    """Represents a set of parameter updates"""
    parameters: Dict[str, Any] = Field(..., description="Parameter name to value mapping")
    design_intent: Optional[str] = Field(None, description="Design intent description")
    constraints: Optional[Dict[str, ParameterConstraint]] = Field(
        None, 
        description="Constraints for each parameter"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls"""
        return self.parameters


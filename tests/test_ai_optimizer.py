"""
Tests for AI Parameter Optimizer
"""

import unittest
from unittest.mock import Mock, patch
from src.ai.optimizer import ParameterOptimizer


class TestParameterOptimizer(unittest.TestCase):
    """Test cases for ParameterOptimizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.current_params = {
            "length": 100.0,
            "width": 50.0,
            "height": 25.0,
            "thickness": 5.0
        }
        self.design_intent = "Minimize weight"
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
    @patch('src.ai.optimizer.openai')
    def test_suggest_parameters_openai(self, mock_openai):
        """Test parameter suggestion with OpenAI"""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"parameters": {"length": 90.0, "thickness": 4.0}}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        optimizer = ParameterOptimizer(provider="openai")
        suggestions = optimizer.suggest_parameters(
            self.current_params,
            self.design_intent
        )
        
        self.assertIsInstance(suggestions, dict)
        self.assertIn("parameters", suggestions or {})
    
    def test_format_parameters(self):
        """Test parameter formatting"""
        optimizer = ParameterOptimizer.__new__(ParameterOptimizer)
        formatted = optimizer._format_parameters(self.current_params)
        
        self.assertIn("length", formatted)
        self.assertIn("100.0", formatted)


if __name__ == '__main__':
    unittest.main()


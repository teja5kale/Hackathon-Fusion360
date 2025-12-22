"""
Simple web UI example (Future Scope)
This demonstrates a basic Flask web interface for parameter inputs
"""

from flask import Flask, render_template_string, request, jsonify
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fusion360.client import Fusion360Client
from src.ai.optimizer import ParameterOptimizer

app = Flask(__name__)

# Initialize clients (in production, use proper initialization)
try:
    fusion_client = Fusion360Client()
    ai_optimizer = ParameterOptimizer()
except Exception as e:
    print(f"Warning: Could not initialize clients: {e}")
    fusion_client = None
    ai_optimizer = None


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI-Assisted Parametric Design</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 8px; margin-top: 5px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>AI-Assisted Parametric Design Automation</h1>
    <h2>Team: AI Catalysts</h2>
    
    <form id="designForm">
        <div class="form-group">
            <label>Project ID:</label>
            <input type="text" name="project_id" required>
        </div>
        
        <div class="form-group">
            <label>Design ID:</label>
            <input type="text" name="design_id" required>
        </div>
        
        <div class="form-group">
            <label>Design Intent:</label>
            <textarea name="design_intent" rows="3" required 
                placeholder="e.g., Minimize weight while maintaining structural integrity"></textarea>
        </div>
        
        <button type="submit">Get AI Suggestions</button>
    </form>
    
    <div id="result" class="result" style="display:none;"></div>
    
    <script>
        document.getElementById('designForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = 'Processing...';
            
            try {
                const response = await fetch('/optimize', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                resultDiv.innerHTML = '<h3>AI Suggestions:</h3><pre>' + 
                    JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                resultDiv.innerHTML = '<p style="color:red;">Error: ' + error.message + '</p>';
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Render main page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/optimize', methods=['POST'])
def optimize():
    """Handle optimization request"""
    if not fusion_client or not ai_optimizer:
        return jsonify({'error': 'Clients not initialized'}), 500
    
    try:
        data = request.json
        project_id = data['project_id']
        design_id = data['design_id']
        design_intent = data['design_intent']
        
        # Load model
        model = fusion_client.load_model(project_id, design_id)
        
        # Get current parameters
        current_params = model.get_parameters()
        
        # Get AI suggestions
        optimized_params = ai_optimizer.suggest_parameters(
            current_parameters=current_params,
            design_intent=design_intent
        )
        
        # Get explanation
        explanation = ai_optimizer.explain_suggestions(
            current_parameters=current_params,
            suggested_parameters=optimized_params,
            design_intent=design_intent
        )
        
        return jsonify({
            'current_parameters': current_params,
            'suggested_parameters': optimized_params,
            'explanation': explanation
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting web UI server...")
    print("Visit http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)


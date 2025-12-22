# Installation Guide: Fusion 360 Add-in

## Quick Installation

### Step 1: Locate Fusion 360 Add-ins Folder

**Windows:**
```
%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns
```
Or navigate to:
```
C:\Users\YourUsername\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns
```

**Mac:**
```
~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns
```

### Step 2: Copy Add-in Folder

1. Copy the entire `fusion360_addin` folder to the AddIns directory
2. The structure should be:
   ```
   AddIns/
     fusion360_addin/
       manifest.json
       ai_parameter_optimizer/
         __init__.py
         commands/
           ApplyAIParameters.py
           GetAISuggestions.py
   ```

### Step 3: Update Paths

Edit the following files and update the `project_root` path:

1. `fusion360_addin/ai_parameter_optimizer/commands/ApplyAIParameters.py`
   - Line ~15: Update `project_root` to your project directory

2. `fusion360_addin/ai_parameter_optimizer/commands/GetAISuggestions.py`
   - Line ~15: Update `project_root` to your project directory

Example:
```python
project_root = r"D:\Hackathon"  # Update this
```

### Step 4: Install Python Dependencies

Fusion 360 uses its own Python environment. You need to install dependencies there:

**Option A: Using Fusion 360's Python**

1. Find Fusion 360's Python executable:
   - Usually in: `C:\Users\YourName\AppData\Local\Autodesk\webdeploy\production\...\Python\python.exe`

2. Install packages:
   ```bash
   "C:\path\to\fusion360\python.exe" -m pip install openai requests python-dotenv
   ```

**Option B: Copy Packages**

1. Install packages in your main Python:
   ```bash
   pip install openai requests python-dotenv
   ```

2. Copy packages to Fusion 360's site-packages directory

### Step 5: Configure Environment Variables

Set environment variables for API keys:

**Windows:**
```cmd
setx OPENAI_API_KEY "your_key_here"
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY="your_key_here"
```

Or create a `.env` file in the project root (if using python-dotenv).

### Step 6: Enable Add-in in Fusion 360

1. Open Fusion 360
2. Go to **Utilities** → **Add-Ins** → **Add-Ins**
3. Find **"AI Parameter Optimizer"**
4. Click **Run** or check **Run on Startup**

### Step 7: Test

1. Open a Fusion 360 design with user parameters
2. Look for new buttons in the **Modify** panel:
   - **Get AI Suggestions**
   - **Apply AI Parameters**
3. Click one to test

## Alternative: Standalone Script

If add-in installation is complex, use the standalone script:

1. Copy `apply_ai_parameters.py` to Fusion 360's scripts folder
2. Update the path in the script (line ~20)
3. Run via **Utilities** → **Scripts and Add-Ins** → **Scripts**

## Troubleshooting

### Add-in doesn't appear

- Check `manifest.json` is valid JSON
- Verify folder structure matches expected format
- Check Fusion 360 version compatibility

### "Module not found" errors

- Verify `project_root` path is correct
- Ensure project's `src` directory is accessible
- Check Python path includes project directory

### "AI optimizer not available"

- Verify dependencies are installed in Fusion 360's Python
- Check API keys are set correctly
- Test import manually in Fusion 360's Python console

### Parameters not updating

- Ensure design has user parameters (not just model parameters)
- Check parameter names match exactly
- Verify parameter expressions are valid

## Verification

Test the installation:

1. Open Fusion 360
2. Create a simple design with user parameters:
   - `length = 100 mm`
   - `width = 50 mm`
3. Run "Get AI Suggestions"
4. Enter design intent: "Minimize weight"
5. Verify suggestions appear

## Support

For issues:
1. Check Fusion 360's add-in log files
2. Verify all paths are correct
3. Test AI optimizer independently
4. Check API keys and quotas


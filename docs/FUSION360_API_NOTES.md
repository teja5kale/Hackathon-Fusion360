# Fusion 360 API Access Notes

## Important Information

### Current Status

The Fusion 360 API for programmatic parameter access is **currently limited**:

1. **Beta Access Required**: The Fusion 360 API endpoints for parametric models may require beta access
2. **Different API Structure**: Fusion 360 cloud projects use a different API structure than Data Management API
3. **URN-Based Access**: Fusion 360 items are accessed via URNs (Uniform Resource Names), not simple IDs

### Project ID Mismatch

The project ID visible in Autodesk 360 URLs (e.g., `202512191028137901`) is **NOT** the same as the API project ID used by Autodesk Platform Services.

### URL Structure

Autodesk 360 URLs contain:
- **Project ID**: Visible in URL (e.g., `202512191028137901`)
- **Folder URN**: Base64-encoded (e.g., `dXJuOmFkc2sud2lwcHJvZDpmcy5mb2xkZXI6...`)
- **Item URN**: Base64-encoded design/item identifier (e.g., `dXJuOmFkc2sud2lwcHJvZDpkbS5saW5lYWdl...`)

### Solutions

#### Option 1: Use Fusion 360 Local API (Recommended for Hackathon)

If you have Fusion 360 installed locally, you can use the **Fusion 360 Local API**:

```python
# Fusion 360 Local API (requires Fusion 360 running)
import adsk.core, adsk.fusion

app = adsk.core.Application.get()
design = app.activeProduct
params = design.userParameters
```

#### Option 2: Request Beta Access

1. Go to [Autodesk Platform Services](https://aps.autodesk.com/)
2. Check if Fusion 360 API beta is available
3. Request access if needed

#### Option 3: Use AI Demo (Current Workaround)

The AI optimization component works independently:

```bash
python examples/ai_demo.py
```

This demonstrates the AI parameter optimization without requiring Fusion 360 API access.

### Required Scopes

Ensure your APS app has these scopes:
- `data:read` - Read data
- `data:write` - Write data  
- `code:all` - **Required for Fusion 360 API access**
- `account:read` - May be needed for hub access

### API Endpoints

The correct endpoints for Fusion 360 may be:
- `/fusion/v1/...` - Fusion 360 specific API (beta)
- `/data/v1/...` - Data Management API (for files, not parametric models)

### Current Limitations

1. **404 Errors**: Project IDs from URLs don't match API project IDs
2. **No Hubs**: May not have access to hubs containing projects
3. **API Availability**: Fusion 360 parametric API may not be publicly available yet

### Workaround for Demo

For the hackathon demo, you can:

1. **Show AI Optimization**: Use `examples/ai_demo.py` to demonstrate AI parameter suggestions
2. **Mock Fusion 360**: Show how the system would work with mock parameters
3. **Local API**: If Fusion 360 is installed, use local API for actual model access

### Next Steps

1. Verify APS app scopes include `code:all`
2. Check if Fusion 360 API beta access is available
3. Consider using Fusion 360 Local API for the demo
4. Use AI demo to show optimization capabilities

## References

- [Autodesk Platform Services](https://aps.autodesk.com/)
- [Fusion 360 API Documentation](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-8A2C4ECD-7EDE-4B73-BF51-22677A3160F0)
- [Data Management API](https://aps.autodesk.com/en/docs/data/v1/overview/)


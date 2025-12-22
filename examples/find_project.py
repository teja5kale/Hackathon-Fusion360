"""
Find the correct project ID for API access
Helps discover projects accessible via APS API
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fusion360.client import Fusion360Client


def find_projects():
    """Find accessible projects via APS API"""
    
    print("=" * 70)
    print("Finding Accessible Projects")
    print("=" * 70)
    print()
    
    try:
        client = Fusion360Client()
        print("[OK] Client initialized\n")
        
        # Method 1: List hubs (for team/personal hubs)
        print("Method 1: Listing hubs...")
        print("-" * 70)
        try:
            hubs = client.list_projects()  # This lists hubs
            print(f"Found {len(hubs)} hub(s)\n")
            
            if len(hubs) == 0:
                print("⚠️  No hubs found. This could mean:")
                print("   - Your account doesn't have access to hubs")
                print("   - You need different API scopes")
                print("   - The project is in a different location")
                print()
            
            for hub in hubs:
                hub_id = hub.get('id', 'N/A')
                hub_type = hub.get('type', 'N/A')
                hub_name = hub.get('attributes', {}).get('name', 'N/A')
                
                print(f"Hub: {hub_name}")
                print(f"  ID: {hub_id}")
                print(f"  Type: {hub_type}")
                
                # Try to list projects in this hub
                try:
                    projects_response = client._make_request(
                        'GET',
                        f'/project/v1/hubs/{hub_id}/projects'
                    )
                    projects = projects_response.json().get('data', [])
                    print(f"  Projects: {len(projects)}")
                    
                    for proj in projects[:3]:
                        proj_id = proj.get('id', 'N/A')
                        proj_name = proj.get('attributes', {}).get('name', 'N/A')
                        print(f"    - {proj_name} (ID: {proj_id})")
                    
                except Exception as e:
                    print(f"  Could not list projects: {e}")
                
                print()
        
        except Exception as e:
            print(f"[X] Error: {e}")
            if hasattr(e, 'response'):
                try:
                    error_detail = e.response.json()
                    print(f"Details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Status: {e.response.status_code}")
        
        # Method 2: Try Data Management API directly
        print("\n" + "=" * 70)
        print("Method 2: Data Management API")
        print("=" * 70)
        print("\nNote: For Fusion 360 cloud projects, you may need to:")
        print("1. Access via Fusion 360 API (not Data Management API)")
        print("2. Use the URN directly instead of project ID")
        print("3. Ensure your app has 'code:all' scope for Fusion 360 access")
        print()
        
        # Check current scopes
        print("Current OAuth scopes:")
        print(f"  {', '.join(client.oauth_client.SCOPES)}")
        print()
        
        print("=" * 70)
        print("Recommendations:")
        print("=" * 70)
        print("""
For Fusion 360 cloud projects, the API structure is different:

1. Fusion 360 API uses URNs (Uniform Resource Names) directly
2. The project ID in the URL may not match the API project ID
3. You may need to:
   - Use Fusion 360 API endpoints (not Data Management API)
   - Access items via their URN directly
   - Ensure 'code:all' scope is enabled in your APS app

The Fusion 360 API for parametric models is currently in beta/limited access.
You may need to:
- Request access to Fusion 360 API beta
- Use Fusion 360's local API if available
- Or use the web UI for parameter updates

For now, the AI optimization demo (examples/ai_demo.py) works without
Fusion 360 API access and shows how the optimization would work.
        """)
        
    except Exception as e:
        print(f"[X] Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    find_projects()


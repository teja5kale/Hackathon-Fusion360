"""
API Discovery Script
Helps discover the correct API endpoints for accessing Fusion 360 projects
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fusion360.client import Fusion360Client


def discover_api_structure():
    """Discover the API structure for accessing Fusion 360 projects"""
    
    print("=" * 70)
    print("Fusion 360 API Discovery")
    print("=" * 70)
    print()
    
    try:
        client = Fusion360Client()
        print("[OK] Client initialized")
        print()
        
        # Step 1: List hubs
        print("Step 1: Listing hubs...")
        print("-" * 70)
        try:
            hubs = client.list_projects()  # This actually lists hubs
            print(f"[OK] Found {len(hubs)} hub(s)")
            for i, hub in enumerate(hubs[:3], 1):  # Show first 3
                hub_id = hub.get('id', 'N/A')
                hub_type = hub.get('type', 'N/A')
                hub_name = hub.get('attributes', {}).get('name', 'N/A')
                print(f"  {i}. Hub ID: {hub_id}")
                print(f"     Type: {hub_type}")
                print(f"     Name: {hub_name}")
                print()
            
            if len(hubs) > 0:
                first_hub = hubs[0]
                hub_id = first_hub.get('id')
                print(f"Using first hub: {hub_id}")
                print()
                
                # Step 2: List projects in hub
                print("Step 2: Listing projects in hub...")
                print("-" * 70)
                try:
                    # Try Data Management API structure
                    response = client._make_request(
                        'GET',
                        f'/project/v1/hubs/{hub_id}/projects'
                    )
                    projects = response.json().get('data', [])
                    print(f"[OK] Found {len(projects)} project(s)")
                    for i, project in enumerate(projects[:5], 1):
                        proj_id = project.get('id', 'N/A')
                        proj_name = project.get('attributes', {}).get('name', 'N/A')
                        print(f"  {i}. Project ID: {proj_id}")
                        print(f"     Name: {proj_name}")
                        print()
                except Exception as e:
                    print(f"[!] Error listing projects: {e}")
                    print("    Trying alternative endpoint structure...")
                    
                    # Try alternative structure
                    try:
                        response = client._make_request(
                            'GET',
                            f'/data/v1/projects/{hub_id}'
                        )
                        print(f"[OK] Alternative endpoint works!")
                        print(json.dumps(response.json(), indent=2)[:500])
                    except Exception as e2:
                        print(f"[!] Alternative also failed: {e2}")
                
        except Exception as e:
            print(f"[X] Error listing hubs: {e}")
            print(f"    Response: {str(e)}")
            if hasattr(e, 'response'):
                try:
                    error_detail = e.response.json()
                    print(f"    Details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"    Status: {e.response.status_code}")
                    print(f"    Text: {e.response.text[:200]}")
        
        print()
        print("=" * 70)
        print("Testing specific project access...")
        print("=" * 70)
        
        # Test the specific project ID from URL
        project_id = "202512191028137901"
        design_id = "WhYhZOzcT1q_dckVtEvHzg"
        
        print(f"\nProject ID: {project_id}")
        print(f"Design ID: {design_id}")
        print()
        
        # Try different endpoint structures
        endpoints_to_try = [
            f'/project/v1/projects/{project_id}',
            f'/project/v1/projects/{project_id}/items',
            f'/project/v1/projects/{project_id}/items/{design_id}',
            f'/data/v1/projects/{project_id}',
            f'/data/v1/projects/{project_id}/items',
            f'/data/v1/projects/{project_id}/items/{design_id}',
        ]
        
        for endpoint in endpoints_to_try:
            print(f"Trying: {endpoint}")
            try:
                response = client._make_request('GET', endpoint)
                print(f"  [OK] Status: {response.status_code}")
                data = response.json()
                print(f"  Response keys: {list(data.keys())[:5]}")
                if 'data' in data:
                    print(f"  Data items: {len(data.get('data', []))}")
            except Exception as e:
                status = getattr(e.response, 'status_code', 'N/A') if hasattr(e, 'response') else 'N/A'
                print(f"  [X] Status: {status}, Error: {str(e)[:100]}")
            print()
        
    except Exception as e:
        print(f"[X] Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    discover_api_structure()


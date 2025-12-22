"""
Parse Autodesk 360 URL and extract proper IDs for API access
"""

import sys
import base64
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fusion360.client import Fusion360Client


def parse_autodesk_url(url: str):
    """Parse Autodesk 360 URL to extract URNs and IDs"""
    
    print("=" * 70)
    print("Autodesk 360 URL Parser")
    print("=" * 70)
    print(f"\nURL: {url}\n")
    
    # Extract base64 URNs from URL
    urn_pattern = r'dXJu[^/]+'
    urns = re.findall(urn_pattern, url)
    
    print("Found URNs in URL:")
    print("-" * 70)
    for i, urn in enumerate(urns, 1):
        print(f"{i}. {urn}")
        try:
            # Decode base64 URN
            decoded = base64.urlsafe_b64decode(urn + '==')  # Add padding
            decoded_str = decoded.decode('utf-8', errors='ignore')
            print(f"   Decoded: {decoded_str[:100]}")
            
            # Extract IDs from decoded URN
            if 'folder' in decoded_str.lower():
                print("   Type: Folder")
            elif 'lineage' in decoded_str.lower() or 'dm.' in decoded_str.lower():
                print("   Type: Item/Design")
                # Extract item ID
                item_match = re.search(r':([^:]+)$', decoded_str)
                if item_match:
                    print(f"   Item ID: {item_match.group(1)}")
        except Exception as e:
            print(f"   Could not decode: {e}")
        print()
    
    # Extract project ID
    project_match = re.search(r'/projects/([^/]+)', url)
    if project_match:
        project_id = project_match.group(1)
        print(f"Project ID from URL: {project_id}")
        print()
    
    # Try to use Data Management API with URNs
    if len(urns) >= 2:
        folder_urn = urns[0]
        item_urn = urns[1]
        
        print("=" * 70)
        print("Trying Data Management API access")
        print("=" * 70)
        
        try:
            client = Fusion360Client()
            
            # Try to get item details using URN
            print(f"\nTrying to access item with URN: {item_urn[:50]}...")
            
            # Data Management API endpoint for item details
            # Need to URL encode the URN
            import urllib.parse
            encoded_urn = urllib.parse.quote(item_urn, safe='')
            
            endpoints_to_try = [
                f'/data/v1/projects/{project_id}/items',
                f'/data/v1/projects/{project_id}/items/{item_urn}',
                f'/data/v1/projects/{project_id}/items/{encoded_urn}',
                f'/modelderivative/v2/designdata/{item_urn}/metadata',
            ]
            
            for endpoint in endpoints_to_try:
                print(f"\nTrying: {endpoint}")
                try:
                    response = client._make_request('GET', endpoint)
                    print(f"  [OK] Status: {response.status_code}")
                    data = response.json()
                    print(f"  Response: {str(data)[:200]}")
                    break
                except Exception as e:
                    status = getattr(e.response, 'status_code', 'N/A') if hasattr(e, 'response') else 'N/A'
                    print(f"  [X] Status: {status}")
                    if hasattr(e, 'response') and e.response.status_code != 404:
                        try:
                            error_detail = e.response.json()
                            print(f"  Error: {str(error_detail)[:200]}")
                        except:
                            print(f"  Error: {e.response.text[:200]}")
            
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    url = "https://cctech82.autodesk360.com/g/projects/202512191028137901/data/dXJuOmFkc2sud2lwcHJvZDpmcy5mb2xkZXI6Y28uZzh1SHRBVk1TLTJPRTlITWx3Z1BNQQ/dXJuOmFkc2sud2lwcHJvZDpkbS5saW5lYWdlOldoYlhaT3pjVDFxX2Rja1R0RXZIemc/overview"
    parse_autodesk_url(url)


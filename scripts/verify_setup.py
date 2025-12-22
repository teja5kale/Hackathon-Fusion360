"""
Setup verification script
Checks if all dependencies and configurations are correct
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[X] Python 3.8+ required")
        return False
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'requests',
        'oauthlib',
        'requests_oauthlib',
        'pydantic',
        'dotenv',
        'yaml'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package}")
        except ImportError:
            print(f"[X] {package} - not installed")
            missing.append(package)
    
    # Check optional AI providers
    try:
        import openai
        print("[OK] openai (optional)")
    except ImportError:
        print("[!] openai (optional) - not installed")
    
    try:
        import anthropic
        print("[OK] anthropic (optional)")
    except ImportError:
        print("[!] anthropic (optional) - not installed")
    
    return len(missing) == 0

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("[X] .env file not found")
        print("   Create it from .env.example")
        return False
    
    print("[OK] .env file exists")
    
    # Check for required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'APS_CLIENT_ID',
        'APS_CLIENT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"[X] {var} not set in .env")
        else:
            print(f"[OK] {var} is set")
    
    # Check AI provider
    has_openai = bool(os.getenv('OPENAI_API_KEY'))
    has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
    
    if has_openai:
        print("[OK] OPENAI_API_KEY is set")
    elif has_anthropic:
        print("[OK] ANTHROPIC_API_KEY is set")
    else:
        print("[!] No AI provider API key set (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
    
    return len(missing_vars) == 0

def check_project_structure():
    """Check if project structure is correct"""
    required_dirs = [
        'src',
        'src/auth',
        'src/fusion360',
        'src/ai',
        'src/models',
        'examples',
        'config',
        'docs'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"[OK] {dir_path}/")
        else:
            print(f"[X] {dir_path}/ - missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all checks"""
    print("=" * 60)
    print("Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Configuration", check_env_file),
        ("Project Structure", check_project_structure)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    if all(results):
        print("[OK] All checks passed! You're ready to go.")
        return 0
    else:
        print("[X] Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


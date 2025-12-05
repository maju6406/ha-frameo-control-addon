#!/usr/bin/env python3
"""
Quick test script to verify the package installation and basic functionality
"""

import sys

def test_imports():
    """Test that package can be imported"""
    print("Testing imports...")
    try:
        import frameo_control
        print(f"✓ frameo_control imported successfully (version {frameo_control.__version__})")
        
        from frameo_control import api
        print("✓ API module imported")
        
        from frameo_control import cli
        print("✓ CLI module imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_entry_points():
    """Test that entry points are available"""
    print("\nTesting entry points...")
    import subprocess
    
    # Test frameo-api command exists
    try:
        result = subprocess.run(
            ["frameo-api", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 or "frameo" in result.stdout.lower():
            print("✓ frameo-api command available")
        else:
            print("✗ frameo-api command failed")
            return False
    except FileNotFoundError:
        print("✗ frameo-api command not found")
        return False
    except Exception as e:
        print(f"✗ Error testing frameo-api: {e}")
        return False
    
    # Test frameo-cli command exists
    try:
        result = subprocess.run(
            ["frameo-cli", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 or "frameo cli" in result.stdout.lower():
            print("✓ frameo-cli command available")
            print(f"  {result.stdout.strip()}")
        else:
            print("✗ frameo-cli command failed")
            return False
    except FileNotFoundError:
        print("✗ frameo-cli command not found")
        return False
    except Exception as e:
        print(f"✗ Error testing frameo-cli: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that required dependencies are installed"""
    print("\nTesting dependencies...")
    required = ["quart", "adb_shell", "usb1", "requests", "docopt"]
    
    all_present = True
    for module in required:
        try:
            __import__(module)
            print(f"✓ {module} installed")
        except ImportError:
            print(f"✗ {module} missing")
            all_present = False
    
    return all_present

def main():
    print("=" * 50)
    print("Frameo Control API Package Test")
    print("=" * 50)
    print()
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Entry Points", test_entry_points()))
    results.append(("Dependencies", test_dependencies()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! Package is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

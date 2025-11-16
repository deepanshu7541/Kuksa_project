"""
Helper script to set up and verify SUMO simulation files.
This script can generate the network file if needed.
"""

import os
import sys
import subprocess


def check_sumo_installed():
    """Check if SUMO is installed and accessible."""
    try:
        result = subprocess.run(
            ["sumo", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"[OK] SUMO is installed: {result.stdout.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("[X] SUMO is not installed or not in PATH")
    print("  Please install SUMO from: https://sumo.dlr.de/docs/Downloads.php")
    return False


def check_sumo_files():
    """Check if required SUMO files exist."""
    files = [
        "highway.net.xml",
        "highway.rou.xml",
        "highway.sumocfg"
    ]
    
    all_exist = True
    for file in files:
        path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(path):
            print(f"[OK] {file} exists")
        else:
            print(f"[X] {file} is missing")
            all_exist = False
    
    return all_exist


def validate_sumo_config():
    """Validate SUMO configuration using sumo --check."""
    config_path = os.path.join(os.path.dirname(__file__), "highway.sumocfg")
    
    if not os.path.exists(config_path):
        print(f"[X] Config file not found: {config_path}")
        return False
    
    try:
        result = subprocess.run(
            ["sumo", "-c", config_path, "--no-step-log", "--end", "1"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("[OK] SUMO configuration is valid")
            return True
        else:
            print(f"[X] SUMO configuration has errors:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"[X] Error validating config: {e}")
        return False


def main():
    """Main setup and verification function."""
    print("SUMO Setup Verification")
    print("=" * 40)
    
    sumo_ok = check_sumo_installed()
    files_ok = check_sumo_files()
    
    if sumo_ok and files_ok:
        print("\nValidating configuration...")
        validate_sumo_config()
    
    print("\n" + "=" * 40)
    
    if sumo_ok and files_ok:
        print("[OK] Setup complete! You can run the simulation.")
        print("\nExample command:")
        print("  python -m speedMonitor.sumo_integration --config sumo/highway.sumocfg --threshold 50.0")
    else:
        print("[X] Setup incomplete. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()


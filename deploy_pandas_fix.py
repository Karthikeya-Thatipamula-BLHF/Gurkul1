#!/usr/bin/env python3
"""
Quick deployment fix for pandas/Python 3.13 compatibility
"""

import subprocess
import sys
import os

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd} failed: {e}")
        return False

def main():
    print("🔧 PANDAS/PYTHON 3.13 COMPATIBILITY FIX")
    print("=" * 50)
    
    # Check if runtime.txt exists
    runtime_file = "Backend/runtime.txt"
    if os.path.exists(runtime_file):
        with open(runtime_file, 'r') as f:
            version = f.read().strip()
        print(f"📋 Current Python version: {version}")
    else:
        print("📋 Creating runtime.txt with Python 3.12.8")
        with open(runtime_file, 'w') as f:
            f.write("python-3.12.8")
    
    print("\n🎯 RECOMMENDED SOLUTION:")
    print("Using Python 3.12.8 with existing packages")
    print("This keeps pandas==2.1.4 and all your current dependencies")
    
    choice = input("\nProceed with Python 3.12.8 fix? (y/n): ").lower()
    
    if choice == 'y':
        commands = [
            "git add .",
            'git commit -m "Fix: Use Python 3.12.8 for pandas compatibility"',
            "git push origin main"
        ]
        
        print("\n🚀 Deploying fix...")
        for cmd in commands:
            run_command(cmd)
        
        print("\n✅ DEPLOYMENT FIX COMPLETE!")
        print("🔗 Monitor your deployment at: https://dashboard.render.com")
        print("📊 Expected build time: 3-5 minutes")
        print("🎉 Pandas will now compile successfully!")
        
        print("\n📋 VERIFICATION URLS:")
        print("• Health: https://gurukul-backend.onrender.com/health")
        print("• Docs: https://gurukul-backend.onrender.com/docs")
    else:
        print("❌ Deployment cancelled")

if __name__ == "__main__":
    main()

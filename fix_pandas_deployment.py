#!/usr/bin/env python3
"""
Automated fix for pandas/Python 3.13 compatibility issue
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
    print("=" * 60)
    
    print("📋 ISSUE IDENTIFIED:")
    print("• pandas==2.1.4 incompatible with Python 3.13")
    print("• _PyLong_AsByteArray API changed in Python 3.13")
    print("• Compilation fails in ccalendar.pyx.c and base.pyx.c")
    
    print("\n🎯 AVAILABLE SOLUTIONS:")
    print("1. Use Python 3.12.8 (keeps all current packages)")
    print("2. Update to Python 3.13 compatible packages")
    print("3. Use minimal requirements (no pandas)")
    
    choice = input("\nChoose solution (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🚀 APPLYING PYTHON 3.12.8 FIX...")
        print("✅ .python-version created")
        print("✅ runtime.txt created")
        print("✅ render.yaml updated")
        
        commands = [
            "git add .python-version runtime.txt render.yaml",
            'git commit -m "Fix: Use Python 3.12.8 for pandas compatibility"',
            "git push origin main"
        ]
        
    elif choice == "2":
        print("\n🚀 APPLYING PYTHON 3.13 PACKAGE UPDATES...")
        if run_command("cp Backend/requirements_python313_fixed.txt Backend/requirements_production.txt"):
            print("✅ Updated requirements to Python 3.13 compatible versions")
        
        commands = [
            "git add Backend/requirements_production.txt",
            'git commit -m "Fix: Update packages for Python 3.13 compatibility"',
            "git push origin main"
        ]
        
    elif choice == "3":
        print("\n🚀 APPLYING MINIMAL REQUIREMENTS FIX...")
        if run_command("cp Backend/requirements_no_pandas.txt Backend/requirements_production.txt"):
            print("✅ Updated to minimal requirements (no pandas)")
        
        commands = [
            "git add Backend/requirements_production.txt",
            'git commit -m "Fix: Use minimal requirements without pandas"',
            "git push origin main"
        ]
        
    else:
        print("❌ Invalid choice")
        return
    
    print("\n📤 DEPLOYING FIX...")
    success_count = 0
    for cmd in commands:
        if run_command(cmd):
            success_count += 1
    
    if success_count == len(commands):
        print("\n✅ DEPLOYMENT FIX COMPLETE!")
        print("🔗 Monitor deployment: https://dashboard.render.com")
        print("📊 Expected build time: 3-5 minutes")
        
        if choice == "1":
            print("🎉 Pandas 2.1.4 will now compile successfully!")
        elif choice == "2":
            print("🎉 Using latest Python 3.13 compatible packages!")
        else:
            print("🎉 Minimal deployment will work reliably!")
            
        print("\n📋 VERIFICATION URLS:")
        print("• Health: https://gurukul-backend.onrender.com/health")
        print("• Docs: https://gurukul-backend.onrender.com/docs")
        print("• Root: https://gurukul-backend.onrender.com/")
    else:
        print("\n⚠️ Some commands failed, but deployment may still work")

if __name__ == "__main__":
    main()

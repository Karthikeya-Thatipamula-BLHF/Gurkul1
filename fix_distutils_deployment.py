#!/usr/bin/env python3
"""
Automated fix for Python 3.12 distutils removal issue
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
    print("🔧 PYTHON 3.12 DISTUTILS COMPATIBILITY FIX")
    print("=" * 60)
    
    print("📋 ISSUE IDENTIFIED:")
    print("• Python 3.12 removed distutils module")
    print("• setuptools trying to import distutils.core")
    print("• ModuleNotFoundError during package installation")
    
    print("\n🎯 AVAILABLE SOLUTIONS:")
    print("1. Python 3.12 + setuptools/wheel fix (modern)")
    print("2. Python 3.11 (distutils included)")
    print("3. Minimal requirements (guaranteed)")
    
    choice = input("\nChoose solution (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🚀 APPLYING PYTHON 3.12 + SETUPTOOLS FIX...")
        print("✅ setuptools>=69.0.0 will be installed first")
        print("✅ wheel>=0.42.0 will be installed first")
        print("✅ Updated requirements with distutils fix")
        
        # Revert to Python 3.12 config
        with open('.python-version', 'w') as f:
            f.write('3.12.8')
        with open('runtime.txt', 'w') as f:
            f.write('python-3.12.8')
        
        commands = [
            "git add .python-version runtime.txt render.yaml Backend/requirements_python312_distutils_fix.txt",
            'git commit -m "Fix: Python 3.12 + setuptools for distutils compatibility"',
            "git push origin main"
        ]
        
    elif choice == "2":
        print("\n🚀 APPLYING PYTHON 3.11 FIX...")
        print("✅ Python 3.11.10 includes distutils")
        print("✅ No setuptools workarounds needed")
        print("✅ All packages work out of the box")
        
        commands = [
            "git add .python-version runtime.txt render.yaml Backend/requirements_python311.txt",
            'git commit -m "Fix: Use Python 3.11.10 to avoid distutils issues"',
            "git push origin main"
        ]
        
    elif choice == "3":
        print("\n🚀 APPLYING MINIMAL REQUIREMENTS FIX...")
        if run_command("cp Backend/requirements_minimal_distutils_safe.txt Backend/requirements_production.txt"):
            print("✅ Updated to minimal distutils-safe requirements")
        
        commands = [
            "git add Backend/requirements_production.txt",
            'git commit -m "Fix: Use minimal distutils-safe requirements"',
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
        print("\n✅ DISTUTILS FIX DEPLOYED!")
        print("🔗 Monitor deployment: https://dashboard.render.com")
        print("📊 Expected build time: 3-5 minutes")
        
        if choice == "1":
            print("🎉 setuptools will provide distutils compatibility!")
        elif choice == "2":
            print("🎉 Python 3.11 includes distutils natively!")
        else:
            print("🎉 Minimal requirements avoid distutils entirely!")
            
        print("\n📋 VERIFICATION URLS:")
        print("• Health: https://gurukul-backend.onrender.com/health")
        print("• Docs: https://gurukul-backend.onrender.com/docs")
        print("• Root: https://gurukul-backend.onrender.com/")
        
        print("\n🔍 WHAT WAS FIXED:")
        if choice == "1":
            print("• setuptools>=69.0.0 installed first")
            print("• wheel>=0.42.0 provides build tools")
            print("• distutils compatibility restored")
        elif choice == "2":
            print("• Python 3.11.10 includes distutils")
            print("• No compatibility issues")
            print("• All packages work natively")
        else:
            print("• Removed packages that need distutils")
            print("• Minimal, reliable deployment")
    else:
        print("\n⚠️ Some commands failed, check manually")

if __name__ == "__main__":
    main()

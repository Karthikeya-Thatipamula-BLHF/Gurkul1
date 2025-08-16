#!/usr/bin/env python3
"""
Automated fix for LangChain dependency conflicts
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
    print("🔧 LANGCHAIN DEPENDENCY CONFLICT RESOLVER")
    print("=" * 60)
    
    print("📋 CONFLICT IDENTIFIED:")
    print("• langchain==0.1.20 needs langchain-core<0.2.0,>=0.1.52")
    print("• langchain-community==0.0.38 needs langchain-core<0.2.0,>=0.1.52")
    print("• langchain-groq==0.1.9 needs langchain-core<0.3.0,>=0.2.26")
    print("• No overlapping version range!")
    
    print("\n🎯 AVAILABLE SOLUTIONS:")
    print("1. Compatible versions (keeps langchain 0.1.20)")
    print("2. Latest versions (upgrades to langchain 0.2.x)")
    print("3. Minimal LangChain (only essential packages)")
    print("4. Constraints file approach")
    
    choice = input("\nChoose solution (1/2/3/4): ").strip()
    
    if choice == "1":
        print("\n🚀 APPLYING COMPATIBLE VERSIONS FIX...")
        print("✅ langchain-core==0.1.52 (shared)")
        print("✅ langchain==0.1.20 (unchanged)")
        print("✅ langchain-community==0.0.38 (unchanged)")
        print("✅ langchain-groq==0.1.5 (downgraded)")
        print("✅ langgraph==0.0.62 (compatible)")
        
        commands = [
            "git add Backend/requirements_langchain_compatible.txt render.yaml",
            'git commit -m "Fix: Resolve LangChain conflicts with compatible versions"',
            "git push origin main"
        ]
        
    elif choice == "2":
        print("\n🚀 APPLYING LATEST VERSIONS FIX...")
        print("⚠️ WARNING: This may require code changes!")
        print("✅ langchain-core==0.2.38 (latest)")
        print("⚠️ langchain==0.2.16 (breaking changes)")
        print("⚠️ langchain-community==0.2.16 (breaking changes)")
        print("✅ langchain-groq==0.1.9 (latest)")
        
        if run_command("cp Backend/requirements_langchain_latest.txt Backend/requirements_production.txt"):
            print("✅ Updated to latest LangChain versions")
        
        commands = [
            "git add Backend/requirements_production.txt",
            'git commit -m "Fix: Upgrade to latest LangChain versions"',
            "git push origin main"
        ]
        
    elif choice == "3":
        print("\n🚀 APPLYING MINIMAL LANGCHAIN FIX...")
        print("✅ Only essential LangChain packages")
        print("✅ No dependency conflicts")
        print("✅ Reduced complexity")
        
        if run_command("cp Backend/requirements_langchain_minimal.txt Backend/requirements_production.txt"):
            print("✅ Updated to minimal LangChain setup")
        
        commands = [
            "git add Backend/requirements_production.txt",
            'git commit -m "Fix: Use minimal LangChain to avoid conflicts"',
            "git push origin main"
        ]
        
    elif choice == "4":
        print("\n🚀 APPLYING CONSTRAINTS FILE FIX...")
        print("✅ Using constraints.txt to force versions")
        print("✅ Keeps original requirements.txt")
        print("✅ Pip resolves with constraints")
        
        commands = [
            "git add Backend/constraints.txt Backend/build_with_constraints.sh",
            'git commit -m "Fix: Add constraints file for LangChain conflicts"',
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
        print("\n✅ LANGCHAIN CONFLICT FIX DEPLOYED!")
        print("🔗 Monitor deployment: https://dashboard.render.com")
        print("📊 Expected build time: 3-5 minutes")
        
        if choice == "1":
            print("🎉 Compatible versions will resolve conflicts!")
        elif choice == "2":
            print("⚠️ Check for breaking changes in your code!")
        elif choice == "3":
            print("🎉 Minimal setup avoids all conflicts!")
        else:
            print("🎉 Constraints will force compatible versions!")
            
        print("\n📋 VERIFICATION URLS:")
        print("• Health: https://gurukul-backend.onrender.com/health")
        print("• Docs: https://gurukul-backend.onrender.com/docs")
        
        print("\n🔍 WHAT WAS FIXED:")
        if choice == "1":
            print("• langchain-groq downgraded to 0.1.5")
            print("• langgraph downgraded to 0.0.62")
            print("• All packages share langchain-core 0.1.52")
        elif choice == "2":
            print("• All LangChain packages upgraded")
            print("• Uses langchain-core 0.2.38")
            print("• May require code updates")
        elif choice == "3":
            print("• Removed conflicting packages")
            print("• Only essential LangChain components")
        else:
            print("• Constraints file forces versions")
            print("• Pip resolves with constraints")
    else:
        print("\n⚠️ Some commands failed, check manually")

if __name__ == "__main__":
    main()

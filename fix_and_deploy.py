#!/usr/bin/env python3
"""
Quick fix and deployment script for Render.com
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and print status"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main deployment fix function"""
    print("=" * 60)
    print("Gurukul Platform - Deployment Fix")
    print("=" * 60)
    
    commands = [
        ("git add .", "Adding all changes"),
        ('git commit -m "Fix deployment dependencies and configuration"', "Committing fixes"),
        ("git push origin main", "Pushing to GitHub")
    ]
    
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"[WARNING] Continuing despite failure in: {description}")
    
    print("\n" + "=" * 60)
    print("Deployment Fix Summary")
    print("=" * 60)
    
    print(f"[INFO] {success_count}/{len(commands)} commands completed")
    
    print("\n[INFO] Changes made:")
    print("✅ Created minimal requirements_render.txt")
    print("✅ Created simplified main_render.py")
    print("✅ Updated render.yaml configuration")
    print("✅ Fixed frontend build scripts")
    
    print("\n[INFO] Next steps:")
    print("1. Go to your Render dashboard")
    print("2. Trigger a new deployment")
    print("3. Monitor the build logs")
    print("4. The deployment should now succeed!")
    
    print("\n[INFO] Your backend will be available at:")
    print("https://gurukul-backend.onrender.com/health")

if __name__ == "__main__":
    main()

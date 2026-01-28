import os
import sys
import subprocess
import time

# Force UTF-8 encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

def check_git_status():
    """Checks if there are uncommitted changes."""
    print("🔍 Checking Git status...")
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if result.stdout.strip():
        print("⚠️  Warning: You have uncommitted changes!")
        print(result.stdout)
        confirm = input("Do you want to continue pushing ONLY committed changes? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Deployment aborted.")
            sys.exit(1)
    else:
        print("✅ Git status clean.")

def git_push():
    """Pushes changes to the remote repository."""
    print("\n🚀 Pushing changes to origin/main...")
    try:
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Push successful.")
    except subprocess.CalledProcessError:
        print("❌ Failed to push to git. Please check your network/credentials.")
        sys.exit(1)

def show_server_instructions():
    """Shows manual server deployment instructions after push."""
    print("\n" + "=" * 50)
    print("📋 MANUAL SERVER DEPLOYMENT REQUIRED")
    print("=" * 50)
    print("\n🔗 Step 1: SSH into the server:")
    print("   ssh forex")
    print("\n🔄 Step 2: Run the update script:")
    print("   cd ~/Forex_Agent && bash execution/scripts/update_server.sh")
    print("\n   OR run commands individually:")
    print("   cd ~/Forex_Agent")
    print("   git pull origin main")
    print("   docker compose down && docker compose up -d --build")
    print("\n🏥 Step 3: Verify deployment:")
    print("   docker ps")
    print("   docker logs forex_agent-agent-1 --tail 50")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    print("=== Forex Agent Deploy (Push-Only) ===")
    check_git_status()
    git_push()
    show_server_instructions()
    print("\n✅ Push Complete! Now manually pull on the server.")

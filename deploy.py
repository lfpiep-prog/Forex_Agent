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

def deploy_remote():
    """Triggers the pull and rebuild on the server."""
    print("\n🌍 Connecting to server 'forex' to deploy...")
    
    # Imports here to avoid issues if verification fails early
    try:
        from execution.tools.remote_ops import run_remote_command, rebuild_and_restart
    except ImportError:
        # If running from root, execution is a package
        sys.path.append(os.path.abspath(os.getcwd()))
        from execution.tools.remote_ops import run_remote_command, rebuild_and_restart

    # 1. Git Pull
    print("   ⬇️  Pulling latest code...")
    pull_result = run_remote_command("cd ~/Forex_Agent && git pull")
    if pull_result:
        print(f"      {pull_result}")
    else:
        print("❌ Failed to pull code on server.")
        sys.exit(1)

    # 2. Rebuild and Restart Containers
    print("   nm 🔄 Rebuilding and Restarting Docker containers...")
    restart_result = rebuild_and_restart()
    if restart_result is not None:
        print("✅ Server restarted successfully.")
        if restart_result:
             print(restart_result)
    else:
        print("❌ Failed to restart server.")
        sys.exit(1)

def health_check():
    """Verifies the deployment."""
    try:
        from execution.tools.remote_ops import run_remote_command
    except ImportError:
        sys.path.append(os.path.abspath(os.getcwd()))
        from execution.tools.remote_ops import run_remote_command

    print("\n🏥 Performing Health Check...")
    print("   ⏳ Waiting 15 seconds for service startup...")
    time.sleep(15)
    
    status_output = run_remote_command("docker ps -a --format 'table {{.Names}}\t{{.Status}}'")
    print(status_output)

    if "Up" in str(status_output):
        print("✅ Deployment verified: Services are UP.")
    else:
        print("⚠️  Warning: Services might not be running correctly. Check logs.")

if __name__ == "__main__":
    print("=== Forex Agent Auto-Deploy (Semi-Automated) ===")
    check_git_status()
    git_push()
    deploy_remote()
    health_check()
    print("\n🎉 Deployment Complete!")

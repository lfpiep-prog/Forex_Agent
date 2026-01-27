import os
import sys
import subprocess
import time

# Force UTF-8 encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Ensure tools are importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/tools")
try:
    from remote_ops import run_remote_command, restart_docker_services, get_docker_logs
except ImportError:
    # Fallback if running from root
    sys.path.append(os.path.abspath("tools"))
    from remote_ops import run_remote_command, restart_docker_services, get_docker_logs

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
    """Triggers the pull and restart on the server."""
    print("\n🌍 Connecting to server 'forex' to deploy...")
    
    # 1. Git Pull
    print("   ⬇️  Pulling latest code...")
    pull_result = run_remote_command("cd ~/ForexAgent && git pull")
    if pull_result:
        print(f"      {pull_result}")
    else:
        print("❌ Failed to pull code on server.")
        sys.exit(1)

    # 2. Restart Containers
    print("   🔄 Restarting Docker containers...")
    restart_result = restart_docker_services()
    if restart_result:
        print("✅ Server restarted successfully.")
    else:
        print("❌ Failed to restart server.")
        sys.exit(1)

def health_check():
    """Verifies the deployment."""
    print("\n🏥 Performing Health Check...")
    print("   ⏳ Waiting 10 seconds for service startup...")
    time.sleep(10)
    
    status_output = run_remote_command("docker ps -a --format 'table {{.Names}}\t{{.Status}}'")
    print(status_output)

    if "Up" in status_output:
        print("✅ Deployment verified: Services are UP.")
    else:
        print("⚠️  Warning: Services might not be running correctly. Check logs.")

if __name__ == "__main__":
    print("=== Forex Agent Auto-Deploy ===")
    check_git_status()
    git_push()
    deploy_remote()
    health_check()
    print("\n🎉 Deployment Complete!")

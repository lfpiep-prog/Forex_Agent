import subprocess
import sys
import argparse
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SERVER_ALIAS = "forex"

def run_remote_command(command, alias=SERVER_ALIAS):
    """
    Executes a command on the remote server via SSH.
    """
    ssh_cmd = ["ssh", alias, command]
    try:
        logger.info(f"Executing remote command: {command}")
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None

def restart_docker_services():
    """
    Restarts the Docker services on the remote server.
    """
    logger.info("Restarting Docker services...")
    # Navigate to directory and restart
    cmd = "cd ~/ForexAgent && docker compose restart"
    return run_remote_command(cmd)

def get_docker_logs(service_name="forex_agent", lines=50):
    """
    Fetches the last N lines of logs for a specific service.
    """
    cmd = f"docker logs --tail {lines} {service_name}"
    return run_remote_command(cmd)

def git_pull():
    """
    Pulls the latest changes from the git repository on the server.
    """
    logger.info("Pulling latest changes from git...")
    cmd = "cd ~/ForexAgent && git pull"
    return run_remote_command(cmd)

def get_system_status():
    """
    Checks system status (disk usage, memory, load).
    """
    cmd = "uptime && free -h && df -h /"
    return run_remote_command(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remote Operations Tool for Forex Agent Server")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # Status command
    subparsers.add_parser("status", help="Get system status")

    # Restart command
    subparsers.add_parser("restart", help="Restart Docker services")

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Get service logs")
    logs_parser.add_argument("--service", default="forex_agent", help="Service name (default: forex_agent)")
    logs_parser.add_argument("--lines", type=int, default=50, help="Number of lines to retrieve (default: 50)")

    # Execute arbitrary command
    exec_parser = subparsers.add_parser("exec", help="Execute arbitrary command")
    exec_parser.add_argument("command", help="Command to execute")

    # Update (Git Pull)
    subparsers.add_parser("update", help="Pull latest git changes")

    args = parser.parse_args()

    if args.action == "status":
        print(get_system_status())
    elif args.action == "restart":
        print(restart_docker_services())
    elif args.action == "logs":
        print(get_docker_logs(args.service, args.lines))
    elif args.action == "update":
        print(git_pull())
    elif args.action == "exec":
        print(run_remote_command(args.command))
    else:
        parser.print_help()

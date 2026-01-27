import os
import sys
import argparse

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from remote_ops import run_remote_command, get_docker_logs, get_system_status

def check_disk_space():
    print("Checking disk space...")
    output = run_remote_command("df -h /")
    if output:
        print(output)
        # Simple check for >90% usage
        if "9%" in output or "100%" in output: # Very dumb check but effective for now
             print("WARNING: Disk space might be running low!")
    else:
        print("Failed to check disk space.")

def check_docker_containers():
    print("\nChecking Docker containers...")
    output = run_remote_command("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.State}}'")
    if output:
        print(output)
        if "Exited" in output or "Restarting" in output:
            print("WARNING: Some containers are not running correctly!")
    else:
        print("Failed to check Docker containers.")

def check_logs_for_errors(lines=50):
    print(f"\nChecking last {lines} lines of logs for errors...")
    logs = get_docker_logs("forex_agent", lines=lines)
    if logs:
        error_keywords = ["Error", "Exception", "Traceback", "CRITICAL", "FATAL"]
        found_errors = False
        for line in logs.split('\n'):
            if any(keyword in line for keyword in error_keywords):
                print(f"[ERROR FOUND] {line}")
                found_errors = True
        
        if not found_errors:
            print("No obvious errors found in the recent logs.")
    else:
        print("Failed to retrieve logs.")

def main():
    parser = argparse.ArgumentParser(description="Troubleshoot Forex Agent Server")
    parser.add_argument("--logs", action="store_true", help="Include log check")
    args = parser.parse_args()

    print("=== Starting Remote Troubleshooting ===\n")
    check_disk_space()
    check_docker_containers()
    
    if args.logs:
        check_logs_for_errors()
    
    print("\n=== Troubleshooting Complete ===")

if __name__ == "__main__":
    main()

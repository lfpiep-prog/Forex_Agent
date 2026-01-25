import subprocess
import urllib.request
import urllib.error
import os
import sys
import json
import time

# Force UTF-8 output for Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
MACRO_SERVER_URL = "http://localhost:8000/health"
REQUIRED_FILES = [
    "trade_journal.csv",
    "trades.db",
    "macro_data.db"
]
CONTAINERS = [
    "forex-agent-agent-1",
    "forex-agent-macro-server-1"
]

class SystemCheck:
    def __init__(self):
        self.results = []
        self.passed = True

    def log(self, message, status="INFO"):
        """Print formatted logs."""
        symbols = {
            "INFO": "ℹ️",
            "OK": "✅",
            "FAIL": "❌",
            "WARN": "⚠️"
        }
        print(f"{symbols.get(status, '')} {message}")

    def check_docker_containers(self):
        """Check if required Docker containers are running."""
        print("\n--- Checking Docker Containers ---")
        try:
            # List all running containers
            output = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}"]).decode("utf-8")
            running_containers = output.strip().split("\n")
            
            for container in CONTAINERS:
                # We do a partial match because docker compose might prefix/suffix differently depending on version/folder
                # But typically it's foldername-servicename-number.
                # Let's try to match loosely if exact match fails
                is_running = container in running_containers
                
                if not is_running:
                    # Fallback matching: check if any running container CONTAINS the service name (e.g., 'macro-server')
                    service_name = container.replace("forex-agent-", "").replace("-1", "")
                    match =  any(service_name in c for c in running_containers)
                    if match:
                        is_running = True
                        # Update the name for reporting
                        found_name = next(c for c in running_containers if service_name in c)
                        self.log(f"Container found as '{found_name}' (expected '{container}')", "OK")
                    else:
                        self.log(f"Container '{container}' is NOT running", "FAIL")
                        self.passed = False
                else:
                    self.log(f"Container '{container}' is running", "OK")

        except FileNotFoundError:
            self.log("Docker command not found. Is Docker installed and in PATH?", "FAIL")
            self.passed = False
        except subprocess.CalledProcessError:
            self.log("Failed to execute docker command.", "FAIL")
            self.passed = False

    def check_api_health(self):
        """Check if the Macro Server API is responding."""
        print("\n--- Checking API Health ---")
        try:
            with urllib.request.urlopen(MACRO_SERVER_URL, timeout=5) as response:
                status_code = response.getcode()
                if status_code == 200:
                    data = json.loads(response.read().decode())
                    if data.get("status") == "ok":
                        self.log(f"Macro Server API is healthy ({MACRO_SERVER_URL})", "OK")
                    else:
                        self.log(f"Macro Server API returned unexpected status: {data}", "WARN")
                else:
                    self.log(f"Macro Server API returned status code: {status_code}", "FAIL")
                    self.passed = False
        except urllib.error.URLError as e:
            self.log(f"Cannot connect to Macro Server API: {e}", "FAIL")
            self.passed = False
        except Exception as e:
            self.log(f"Error checking API: {e}", "FAIL")
            self.passed = False

    def check_files(self):
        """Check if critical data files exist."""
        print("\n--- Checking Data Files ---")
        for filename in REQUIRED_FILES:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                self.log(f"File '{filename}' exists ({size} bytes)", "OK")
            else:
                self.log(f"File '{filename}' is MISSING", "FAIL")
                # We don't fail the whole test for missing files if they are created on runtime, 
                # but for a health check it is good to know.
                # Let's consider it a FAIL for now as these are persistent dbs.
                self.passed = False

    def run(self):
        print("🚀 Starting System Health Check...")
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.check_docker_containers()
        self.check_api_health()
        self.check_files()

        print("\n" + "="*30)
        if self.passed:
            print("✅ SYSTEM CHECK PASSED - All systems operational")
            sys.exit(0)
        else:
            print("❌ SYSTEM CHECK FAILED - Issues detected")
            sys.exit(1)

if __name__ == "__main__":
    check = SystemCheck()
    check.run()

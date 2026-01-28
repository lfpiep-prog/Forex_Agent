#!/usr/bin/env python3
"""
Dynamic Analysis & Validator Tool
=================================

This tool dynamically analyzes the current project state (local) and compares it 
with the remote production server. It automatically detects:
1. Docker Services (from docker-compose.yml)
2. Trading Strategies (from execution/strategies/*.py)
3. System Health (via check_system.py)

Usage:
    python -m execution.dynamic_validator
"""

import os
import sys
import yaml
import glob
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("DynamicValidator")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import existing tools
try:
    from execution.tools.remote_ops import run_remote_command
    from execution.scripts.check_system import ComprehensiveHealthCheck
except ImportError as e:
    logger.error(f"Failed to import necessary modules: {e}")
    logger.error("Ensure you are running from the project root or correct package structure.")
    sys.exit(1)

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class DynamicValidator:
    def __init__(self):
        self.local_state = {}
        self.remote_state = {}
        self.comparison = {}

    def _get_local_services(self):
        """Parse docker-compose.yml for defined services (Feature Detection)."""
        compose_file = PROJECT_ROOT / "docker-compose.yml"
        services = []
        if compose_file.exists():
            try:
                with open(compose_file, "r") as f:
                    data = yaml.safe_load(f)
                    if "services" in data:
                        services = list(data["services"].keys())
            except ImportError:
                # Fallback if pyyaml is missing (manual parsing)
                logger.warning("PyYAML not found, using simple parsing for docker-compose.")
                with open(compose_file, "r") as f:
                    for line in f:
                        if line.strip().startswith("#"): continue
                        if ":" in line and line.startswith("  ") and not line.startswith("    "):
                             # Very basic heuristic for service names at indentation level 2
                            parts = line.split(":")
                            services.append(parts[0].strip())
            except Exception as e:
                logger.error(f"Error reading docker-compose.yml: {e}")
        return sorted(services)

    def _get_local_strategies(self):
        """Scan strategies directory for implemented strategies (Feature Detection)."""
        strategies_dir = PROJECT_ROOT / "execution" / "strategies"
        strategies = []
        if strategies_dir.exists():
            for f in strategies_dir.glob("*.py"):
                if f.name != "__init__.py":
                    strategies.append(f.stdout.strip() if hasattr(f, "stdout") else f.stem)
        return sorted(strategies)

    def analyze_local(self):
        """Gather information about the local environment."""
        print(f"{Colors.BLUE}🔍 Analyzing Local Environment...{Colors.ENDC}")
        
        # 1. Detect Features
        services = self._get_local_services()
        strategies = self._get_local_strategies()
        
        # 2. Run Health Check (Quick Mode)
        print("   Running local health check...")
        health = ComprehensiveHealthCheck(full_mode=False)
        # Capture stdout to avoid cluttering main output, or we could modify check_system to return dict
        # For now, we assume local is "dev" and we mostly care about static analysis + simple checks
        # But to be "dynamic", let's actually run the health methods and capture results cleanly
        
        # We'll re-implement a lightweight collection here to avoid parsing stdout
        health_results = {}
        
        # Database checks
        db_path = PROJECT_ROOT / "trades.db"
        health_results["trades_db"] = "Exists" if db_path.exists() else "Missing"
        
        self.local_state = {
            "services": services,
            "strategies": strategies,
            "health": health_results,
            "timestamp": datetime.now().isoformat()
        }
        print(f"   ✅ Detected {len(services)} services and {len(strategies)} strategies.")

    def analyze_remote(self):
        """Connect to server and gather information."""
        print(f"\n{Colors.BLUE}🌍 Analyzing Remote Server (via SSH)...{Colors.ENDC}")
        
        # 1. Check Strategies
        print("   Scanning remote strategies...")
        cmd_strategies = "ls ~/Forex_Agent/execution/strategies/*.py"
        remote_strategies_raw = run_remote_command(cmd_strategies)
        remote_strategies = []
        if remote_strategies_raw:
            for line in remote_strategies_raw.split("\n"):
                if "__init__.py" not in line and line.strip():
                    filename = os.path.basename(line)
                    remote_strategies.append(filename.replace(".py", ""))
        
        # 2. Check Running Containers (Services)
        print("   Checking remote Docker containers...")
        cmd_docker = "docker ps --format '{{.Names}}'"
        remote_containers_raw = run_remote_command(cmd_docker)
        remote_containers = []
        if remote_containers_raw:
            remote_containers = [c.lower() for c in remote_containers_raw.split("\n") if c]

        # 3. Check Remote System Health Script
        # We can try to run the remote health check script if it exists
        print("   Running remote health check...")
        cmd_health = "cd ~/Forex_Agent && python3 -m execution.scripts.check_system --json"
        # Allow non-zero exit code (script returns 1 on failure, but still prints JSON)
        remote_health_json = run_remote_command(cmd_health, raise_on_error=False)
        
        remote_health_status = "Unknown"
        if remote_health_json:
            try:
                # Find JSON part if mixed with logs
                json_start = remote_health_json.find('{')
                json_end = remote_health_json.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    data = json.loads(remote_health_json[json_start:json_end])
                    failed_count = data.get("failed", 0)
                    remote_health_status = "OK" if failed_count == 0 else f"Failed ({failed_count} errors)"
                else:
                    # If no JSON found, it might be an error message (like "unrecognized arguments")
                    if "unrecognized arguments: --json" in remote_health_json:
                        remote_health_status = "Script Outdated (No JSON support)"
                    else:
                         remote_health_status = "Parse Error"
            except:
                remote_health_status = "JSON Error"
        else:
            remote_health_status = "No Output"

        self.remote_state = {
            "strategies": sorted(remote_strategies),
            "containers": remote_containers, # This maps roughly to services
            "health_status": remote_health_status
        }
        print("   ✅ Remote analysis complete.")

    def generate_report(self):
        """Compare local definition vs remote reality."""
        print(f"\n{Colors.BOLD}{'═'*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}📊 DYNAMIC ANALYSIS REPORT{Colors.ENDC}")
        print(f"{Colors.BOLD}{'═'*60}{Colors.ENDC}")

        # --- Strategies Comparison ---
        local_strats = set(self.local_state["strategies"])
        remote_strats = set(self.remote_state["strategies"])
        
        print(f"\n{Colors.BOLD}1. STRATEGIES PARITY{Colors.ENDC}")
        all_strats = sorted(list(local_strats | remote_strats))
        for s in all_strats:
            in_local = s in local_strats
            in_remote = s in remote_strats
            
            icon_local = "✅" if in_local else "❌"
            icon_remote = "✅" if in_remote else "❌"
            
            if in_local and in_remote:
                status = f"{Colors.GREEN}SYNCED{Colors.ENDC}"
            elif in_local and not in_remote:
                status = f"{Colors.YELLOW}PENDING DEPLOY{Colors.ENDC}"
            else:
                status = f"{Colors.RED}REMOTE ONLY{Colors.ENDC}" # Unusual but possible
                
            print(f"   {s:<25} Local: {icon_local}  Remote: {icon_remote}  [{status}]")

        # --- Services Comparison ---
        print(f"\n{Colors.BOLD}2. SERVICES (DOCKER) STATUS{Colors.ENDC}")
        # Note: Local services are from YAML (definitions), Remote are running containers
        # We need flexible matching
        local_services = self.local_state["services"]
        remote_containers = self.remote_state["containers"]
        
        for svc in local_services:
            # Check if any running container matches the service name
            is_running = any(svc in c for c in remote_containers)
            status_color = Colors.GREEN if is_running else Colors.RED
            status_text = "RUNNING" if is_running else "STOPPED/MISSING"
            print(f"   {svc:<25} Defined: ✅  Remote Status: {status_color}{status_text}{Colors.ENDC}")

        # --- Health Summary ---
        print(f"\n{Colors.BOLD}3. SYSTEM HEALTH{Colors.ENDC}")
        r_status = self.remote_state["health_status"]
        r_color = Colors.GREEN if r_status == "OK" else Colors.RED
        print(f"   Remote System Check: {r_color}{r_status}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}{'═'*60}{Colors.ENDC}")

    def run(self):
        self.analyze_local()
        self.analyze_remote()
        self.generate_report()

if __name__ == "__main__":
    validator = DynamicValidator()
    validator.run()

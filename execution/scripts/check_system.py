#!/usr/bin/env python3
# Updated via Agent
"""
Comprehensive System Health Check for Forex Trading Agent
=========================================================

Usage:
    python check_system.py          # Quick check (no external API calls)
    python check_system.py --full   # Full check (includes broker/data provider tests)

Categories tested:
    1. Infrastructure (Docker, Disk, Logs)
    2. Databases (trades.db, macro_data.db)
    3. APIs (Macro Server endpoints)
    4. External Services (Broker, Data Provider, Discord) - only with --full
    5. Configuration (Environment variables)
    6. Application (Trading Engine, Signal Generator)
    7. State (state.json, balance.json)
"""

import subprocess
import urllib.request
import urllib.error
import os
import sys
import json
import time
import sqlite3
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 output for Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Manual .env loading for host execution (where python-dotenv might be missing)
def load_env_manual():
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        if key not in os.environ:
                            os.environ[key] = value
        except Exception as e:
            print(f"Warning: Failed to load .env manually: {e}")

load_env_manual()

# ============================================================================
# CONFIGURATION
# ============================================================================

MACRO_SERVER_URL = "http://localhost:8000"
REQUIRED_FILES = [
    "trade_journal.csv",
    "trades.db",
    "macro_data.db"
]
CONTAINERS = [
    "agent",
    "macro-server"
]
REQUIRED_ENV_VARS = [
    "IG_USERNAME",
    "IG_PASSWORD", 
    "IG_API_KEY",
    "IG_ACC_TYPE"
]
OPTIONAL_ENV_VARS = [
    "DISCORD_WEBHOOK_URL",
    "TWELVEDATA_API_KEY",
    "BRAVE_API_KEY"
]

# ============================================================================
# HELPER CLASSES
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class CheckResult:
    """Result of a single health check"""
    def __init__(self, name: str, passed: bool, message: str, details: str = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details

# ============================================================================
# COMPREHENSIVE HEALTH CHECK CLASS
# ============================================================================

class ComprehensiveHealthCheck:
    def __init__(self, full_mode: bool = False):
        self.full_mode = full_mode
        self.results = []
        self.start_time = None
    
    def log(self, message: str, status: str = "INFO"):
        """Print formatted logs with emoji indicators."""
        symbols = {
            "INFO": "ℹ️ ",
            "OK": "✅",
            "FAIL": "❌",
            "WARN": "⚠️ ",
            "SKIP": "⏭️ "
        }
        colors = {
            "INFO": Colors.CYAN,
            "OK": Colors.GREEN,
            "FAIL": Colors.RED,
            "WARN": Colors.YELLOW,
            "SKIP": Colors.BLUE
        }
        symbol = symbols.get(status, "")
        color = colors.get(status, "")
        print(f"{symbol} {color}{message}{Colors.ENDC}")
    
    def add_result(self, name: str, passed: bool, message: str, details: str = None):
        """Add a check result and log it."""
        self.results.append(CheckResult(name, passed, message, details))
        status = "OK" if passed else "FAIL"
        self.log(f"{name}: {message}", status)
        if details and not passed:
            print(f"   └── {details}")
    
    def section_header(self, title: str, emoji: str):
        """Print a section header."""
        print(f"\n{Colors.BOLD}{'━' * 50}{Colors.ENDC}")
        print(f"{emoji} {Colors.BOLD}{title}{Colors.ENDC}")
        print(f"{Colors.BOLD}{'━' * 50}{Colors.ENDC}")

    # ========================================================================
    # 1. INFRASTRUCTURE CHECKS
    # ========================================================================
    
    def check_docker_containers(self):
        """Check Docker container status, restarts, and resource usage."""
        self.section_header("INFRASTRUCTURE", "📦")
        
        # Check if running inside container
        if os.path.exists("/.dockerenv"):
            self.log("Docker: Running inside container (skipping CLI checks)", "OK")
            self.add_result("Docker", True, "Inside container (implied running)")
            return
        
        try:
            # Get all running containers
            output = subprocess.check_output(
                ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            
            running_containers = {}
            for line in output.split("\n"):
                if "|" in line:
                    name, status = line.split("|", 1)
                    running_containers[name] = status
            
            for expected_container in CONTAINERS:
                # Flexible matching (forex_agent-agent-1, forexagent-agent-1, etc.)
                found = None
                for container_name in running_containers:
                    if expected_container in container_name.lower():
                        found = container_name
                        break
                
                if found:
                    status = running_containers[found]
                    # Check for restart count
                    try:
                        inspect_output = subprocess.check_output(
                            ["docker", "inspect", "--format", "{{.RestartCount}}", found],
                            stderr=subprocess.DEVNULL
                        ).decode("utf-8").strip()
                        restarts = int(inspect_output) if inspect_output else 0
                    except:
                        restarts = 0
                    
                    # Get resource usage
                    try:
                        stats_output = subprocess.check_output(
                            ["docker", "stats", "--no-stream", "--format", "{{.CPUPerc}}|{{.MemUsage}}", found],
                            stderr=subprocess.DEVNULL
                        ).decode("utf-8").strip()
                        if "|" in stats_output:
                            cpu, mem = stats_output.split("|")
                            resource_info = f"CPU: {cpu}, Mem: {mem.split('/')[0].strip()}"
                        else:
                            resource_info = "N/A"
                    except:
                        resource_info = "N/A"
                    
                    restart_warning = f", {restarts} restarts" if restarts > 0 else ""
                    self.add_result(
                        f"Docker: {expected_container}",
                        True,
                        f"Running ({resource_info}{restart_warning})"
                    )
                else:
                    self.add_result(
                        f"Docker: {expected_container}",
                        False,
                        "Container NOT running"
                    )
                    
        except FileNotFoundError:
            self.add_result("Docker", False, "Docker command not found")
        except subprocess.CalledProcessError as e:
            self.add_result("Docker", False, f"Docker command failed: {e}")
    
    def check_filesystem(self):
        """Check disk space and log directory."""
        try:
            # Check disk space (cross-platform)
            if sys.platform == "win32":
                import shutil
                total, used, free = shutil.disk_usage(PROJECT_ROOT)
                free_gb = free / (1024**3)
                percent_free = (free / total) * 100
            else:
                import shutil
                total, used, free = shutil.disk_usage(PROJECT_ROOT)
                free_gb = free / (1024**3)
                percent_free = (free / total) * 100
            
            disk_ok = free_gb > 1  # At least 1GB free
            self.add_result(
                "Disk Space",
                disk_ok,
                f"{free_gb:.1f} GB free ({percent_free:.0f}% available)"
            )
        except Exception as e:
            self.add_result("Disk Space", False, f"Check failed: {e}")
        
        # Check logs directory size
        logs_dir = PROJECT_ROOT / "logs"
        if logs_dir.exists():
            try:
                total_size = sum(f.stat().st_size for f in logs_dir.rglob('*') if f.is_file())
                size_mb = total_size / (1024**2)
                self.add_result("Log Directory", True, f"{size_mb:.1f} MB")
            except Exception as e:
                self.add_result("Log Directory", False, f"Check failed: {e}")
        else:
            self.add_result("Log Directory", True, "Not created yet (OK)")
    
    def check_docker_logs_for_errors(self):
        """Scan recent Docker logs for ERROR/CRITICAL messages."""
        if os.path.exists("/.dockerenv"):
            self.log("Logs: Running inside container (skipping Docker log checks)", "OK")
            return

        for container in CONTAINERS:
            try:
                # Find actual container name
                output = subprocess.check_output(
                    ["docker", "ps", "--format", "{{.Names}}"],
                    stderr=subprocess.DEVNULL
                ).decode("utf-8").strip()
                
                found = None
                for name in output.split("\n"):
                    if container in name.lower():
                        found = name
                        break
                
                if not found:
                    continue
                
                # Get last 100 lines of logs
                logs = subprocess.check_output(
                    ["docker", "logs", "--tail", "100", found],
                    stderr=subprocess.STDOUT
                ).decode("utf-8", errors="ignore")
                
                error_count = logs.lower().count("error")
                critical_count = logs.lower().count("critical")
                traceback_count = logs.lower().count("traceback")
                
                if critical_count > 0 or traceback_count > 0:
                    self.add_result(
                        f"Logs: {container}",
                        False,
                        f"Found {error_count} errors, {critical_count} critical, {traceback_count} tracebacks"
                    )
                elif error_count > 5:
                    self.add_result(
                        f"Logs: {container}",
                        True,
                        f"{error_count} errors (review recommended)"
                    )
                else:
                    self.add_result(
                        f"Logs: {container}",
                        True,
                        "Clean (no critical issues)"
                    )
            except Exception as e:
                pass  # Skip if can't check logs

    # ========================================================================
    # 2. DATABASE CHECKS
    # ========================================================================
    
    def check_databases(self):
        """Check database connectivity and basic integrity."""
        self.section_header("DATABASES", "💾")
        
        # Check trades.db
        trades_db = PROJECT_ROOT / "trades.db"
        if trades_db.exists() and trades_db.stat().st_size > 0:
            try:
                conn = sqlite3.connect(str(trades_db))
                cursor = conn.cursor()
                
                # Get table list
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Get row count from main table
                row_count = 0
                last_entry = "N/A"
                if "trade_results" in tables:
                    cursor.execute("SELECT COUNT(*) FROM trade_results")
                    row_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT timestamp FROM trade_results ORDER BY id DESC LIMIT 1")
                    result = cursor.fetchone()
                    if result:
                        last_entry = result[0]
                
                conn.close()
                
                self.add_result(
                    "trades.db",
                    True,
                    f"Connected ({len(tables)} tables, {row_count} trades, last: {last_entry})"
                )
            except Exception as e:
                self.add_result("trades.db", False, f"Connection failed: {e}")
        else:
            size = trades_db.stat().st_size if trades_db.exists() else 0
            self.add_result("trades.db", False, f"Empty or missing ({size} bytes)")
        
        # Check macro_data.db
        macro_db = PROJECT_ROOT / "macro_data.db"
        if macro_db.exists() and macro_db.stat().st_size > 0:
            try:
                conn = sqlite3.connect(str(macro_db))
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                total_rows = 0
                for table in tables:
                    if table != "sqlite_sequence":
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        total_rows += cursor.fetchone()[0]
                
                conn.close()
                
                self.add_result(
                    "macro_data.db",
                    True,
                    f"Connected ({len(tables)} tables, {total_rows} rows)"
                )
            except Exception as e:
                self.add_result("macro_data.db", False, f"Connection failed: {e}")
        else:
            size = macro_db.stat().st_size if macro_db.exists() else 0
            self.add_result("macro_data.db", False, f"Empty or missing ({size} bytes)")

    # ========================================================================
    # 3. API CHECKS
    # ========================================================================
    
    def check_macro_server_api(self):
        """Check Macro Server API endpoints."""
        self.section_header("APIs", "🌐")
        
        # Health endpoint
        try:
            start = time.time()
            with urllib.request.urlopen(f"{MACRO_SERVER_URL}/health", timeout=5) as response:
                elapsed = (time.time() - start) * 1000
                data = json.loads(response.read().decode())
                if data.get("status") == "ok":
                    self.add_result(
                        "Macro Server /health",
                        True,
                        f"OK (response: {elapsed:.0f}ms)"
                    )
                else:
                    self.add_result(
                        "Macro Server /health",
                        False,
                        f"Unexpected response: {data}"
                    )
        except urllib.error.URLError as e:
            self.add_result("Macro Server /health", False, f"Connection failed: {e.reason}")
        except Exception as e:
            self.add_result("Macro Server /health", False, f"Error: {e}")
        
        # Indicators endpoint
        try:
            with urllib.request.urlopen(f"{MACRO_SERVER_URL}/indicators/", timeout=5) as response:
                data = json.loads(response.read().decode())
                indicator_count = len(data.get("data", [])) if data.get("data") else 0
                self.add_result(
                    "Macro Server /indicators",
                    True,
                    f"OK ({indicator_count} indicators)"
                )
        except urllib.error.URLError as e:
            self.add_result("Macro Server /indicators", False, f"Connection failed")
        except Exception as e:
            self.add_result("Macro Server /indicators", False, f"Error: {e}")

    # ========================================================================
    # 4. EXTERNAL SERVICES (only in --full mode)
    # ========================================================================
    
    def check_broker_connectivity(self):
        """Check IG Broker API connectivity (ONLY in full mode)."""
        if not self.full_mode:
            self.log("Broker: SKIPPED (use --full for API tests)", "SKIP")
            return
        
        try:
            from execution.brokers.ig_broker import IGBroker
            broker = IGBroker()
            
            if broker.connect():
                balance = broker.get_balance()
                if balance:
                    equity = balance.get('equity', 'N/A')
                    acc_type = os.getenv('IG_ACC_TYPE', 'UNKNOWN')
                    self.add_result(
                        "IG Broker",
                        True,
                        f"Connected ({acc_type} Mode, Equity: {equity})"
                    )
                else:
                    self.add_result("IG Broker", False, "Connected but balance retrieval failed")
            else:
                self.add_result("IG Broker", False, "Authentication failed")
        except ImportError:
            self.add_result("IG Broker", False, "Module not found")
        except Exception as e:
            self.add_result("IG Broker", False, f"Error: {e}")
    
    def check_data_provider(self):
        """Check data provider connectivity (ONLY in full mode)."""
        if not self.full_mode:
            self.log("Data Provider: SKIPPED (use --full for API tests)", "SKIP")
            return
        
        try:
            from execution import market_data as data
            
            raw_prices = data.fetch_prices("EURUSD", "H1")
            if raw_prices:
                df = data.normalize(raw_prices)
                if not df.empty:
                    last_candle = df.iloc[-1]['timestamp']
                    self.add_result(
                        "Data Provider",
                        True,
                        f"EURUSD data fetched (last: {last_candle})"
                    )
                else:
                    self.add_result("Data Provider", False, "Empty dataframe returned")
            else:
                self.add_result("Data Provider", False, "No data returned")
        except ImportError as e:
            self.add_result("Data Provider", False, f"Import error: {e}")
        except Exception as e:
            self.add_result("Data Provider", False, f"Error: {e}")
    
    def check_discord_webhook(self):
        """Check Discord webhook configuration."""
        webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        
        if not webhook_url:
            self.add_result("Discord Webhook", True, "Not configured (optional)")
            return
        
        if webhook_url.startswith("https://discord.com/api/webhooks/"):
            self.add_result("Discord Webhook", True, "Configured (URL valid format)")
        else:
            self.add_result("Discord Webhook", False, "Invalid URL format")

    # ========================================================================
    # 5. CONFIGURATION CHECKS
    # ========================================================================
    
    def check_configuration(self):
        """Check environment variables and configuration."""
        self.section_header("CONFIGURATION", "⚙️")
        
        # Check required env vars
        missing_required = []
        for var in REQUIRED_ENV_VARS:
            if not os.getenv(var):
                missing_required.append(var)
        
        if missing_required:
            self.add_result(
                "Required Env Vars",
                False,
                f"Missing: {', '.join(missing_required)}"
            )
        else:
            self.add_result(
                "Required Env Vars",
                True,
                f"All {len(REQUIRED_ENV_VARS)} required vars set"
            )
        
        # Check optional env vars
        set_optional = [var for var in OPTIONAL_ENV_VARS if os.getenv(var)]
        self.add_result(
            "Optional Env Vars",
            True,
            f"{len(set_optional)}/{len(OPTIONAL_ENV_VARS)} configured"
        )
        
        # Check strategy configuration
        try:
            from execution.config import config
            strategy = getattr(config, 'STRATEGY', 'UNKNOWN')
            symbol = getattr(config, 'SYMBOL', 'UNKNOWN')
            self.add_result(
                "Trading Config",
                True,
                f"Strategy: {strategy}, Symbol: {symbol}"
            )
        except Exception as e:
            self.add_result("Trading Config", False, f"Load failed: {e}")

    # ========================================================================
    # 6. APPLICATION CHECKS
    # ========================================================================
    
    def check_application(self):
        """Check trading engine and signal generator."""
        self.section_header("APPLICATION", "🤖")
        
        # Check Trading Engine import
        try:
            from execution.engine import TradingEngine
            engine = TradingEngine()
            self.add_result("Trading Engine", True, "Initialized")
        except Exception as e:
            self.add_result("Trading Engine", False, f"Init failed: {e}")
        
        # Check Signal Generator
        try:
            from execution.generate_signals import SignalGenerator
            from execution.config import config
            
            generator = SignalGenerator(
                getattr(config, 'STRATEGY', 'baseline_sma_cross'),
                getattr(config, 'STRATEGY_PARAMS', {})
            )
            self.add_result("Signal Generator", True, "Initialized")
        except Exception as e:
            self.add_result("Signal Generator", False, f"Init failed: {e}")

    # ========================================================================
    # 7. STATE CHECKS
    # ========================================================================
    
    def check_state(self):
        """Check state and balance files."""
        self.section_header("STATE", "📊")
        
        # Check state.json
        state_file = PROJECT_ROOT / "execution" / "state.json"
        if state_file.exists():
            try:
                with open(state_file) as f:
                    state = json.load(f)
                
                processed_count = 0
                last_candle = "N/A"
                for symbol_data in state.get("processed_candles", {}).values():
                    for tf_data in symbol_data.values():
                        processed_count += len(tf_data)
                        if tf_data:
                            last_candle = max(tf_data)
                
                self.add_result(
                    "state.json",
                    True,
                    f"Valid ({processed_count} candles processed, last: {last_candle})"
                )
            except Exception as e:
                self.add_result("state.json", False, f"Invalid: {e}")
        else:
            self.add_result("state.json", True, "Not created yet (OK for fresh start)")
        
        # Check balance.json
        balance_file = PROJECT_ROOT / "balance.json"
        if balance_file.exists():
            try:
                with open(balance_file) as f:
                    balance = json.load(f)
                
                equity = balance.get("equity", "N/A")
                self.add_result("balance.json", True, f"Valid (Equity: {equity})")
            except Exception as e:
                self.add_result("balance.json", False, f"Invalid: {e}")
        else:
            self.add_result("balance.json", True, "Not created yet (OK)")
        
        # Check trade_journal.csv
        journal_file = PROJECT_ROOT / "trade_journal.csv"
        if journal_file.exists():
            try:
                line_count = sum(1 for _ in open(journal_file))
                self.add_result(
                    "trade_journal.csv",
                    True,
                    f"Exists ({line_count} lines)"
                )
            except Exception as e:
                self.add_result("trade_journal.csv", False, f"Read failed: {e}")
        else:
            self.add_result("trade_journal.csv", True, "Not created yet (OK)")

    # ========================================================================
    # MAIN RUN METHOD
    # ========================================================================
    
    def run(self):
        """Run all health checks and generate report."""
        self.start_time = time.time()
        
        print(f"\n{Colors.BOLD}{'═' * 50}{Colors.ENDC}")
        print(f"🚀 {Colors.BOLD}Comprehensive System Health Check{Colors.ENDC}")
        print(f"{Colors.BOLD}{'═' * 50}{Colors.ENDC}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'FULL (includes external API checks)' if self.full_mode else 'QUICK (no external API calls)'}")
        
        # Run all checks
        self.check_docker_containers()
        self.check_filesystem()
        self.check_docker_logs_for_errors()
        
        self.check_databases()
        
        self.check_macro_server_api()
        
        self.section_header("EXTERNAL SERVICES", "🔌")
        self.check_broker_connectivity()
        self.check_data_provider()
        self.check_discord_webhook()
        
        self.check_configuration()
        
        self.check_application()
        
        self.check_state()
        
        # Summary
        elapsed = time.time() - self.start_time
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)
        
        print(f"\n{Colors.BOLD}{'═' * 50}{Colors.ENDC}")
        if failed == 0:
            print(f"✅ {Colors.GREEN}{Colors.BOLD}SYSTEM CHECK PASSED{Colors.ENDC}")
        else:
            print(f"❌ {Colors.RED}{Colors.BOLD}SYSTEM CHECK FAILED{Colors.ENDC}")
        print(f"{Colors.BOLD}{'═' * 50}{Colors.ENDC}")
        print(f"Results: {passed}/{total} checks passed ({failed} failed)")
        print(f"Duration: {elapsed:.1f} seconds")
        
        if failed > 0:
            print(f"\n{Colors.RED}Failed checks:{Colors.ENDC}")
            for r in self.results:
                if not r.passed:
                    print(f"  ❌ {r.name}: {r.message}")
        
        sys.exit(0 if failed == 0 else 1)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Comprehensive System Health Check for Forex Trading Agent"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full checks including external API calls (broker, data provider)"
    )
    args = parser.parse_args()
    
    check = ComprehensiveHealthCheck(full_mode=args.full)
    check.run()

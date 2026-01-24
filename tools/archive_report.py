
import os
import sys

# Add project root to path to find tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.notebook_logger import log_to_notebook

REPORT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Statusbericht_Forex_Agent.md'))

def archive_report():
    if not os.path.exists(REPORT_PATH):
        print(f"Error: Report file not found at {REPORT_PATH}")
        return

    with open(REPORT_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Log it
    output_path = log_to_notebook("Status_Report_v1", content)
    
    if output_path:
        print(f"Success: Archived report to {output_path}")
    else:
        print("Error: Failed to archive report.")

if __name__ == "__main__":
    archive_report()

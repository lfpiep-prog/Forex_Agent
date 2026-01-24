
import sys
import os
sys.path.append(os.getcwd())
try:
    from execution.config import config
    print(f"DATA_PROVIDER: {config.DATA_PROVIDER}")
    print(f"BROKER: {config.BROKER}")
except Exception as e:
    print(e)

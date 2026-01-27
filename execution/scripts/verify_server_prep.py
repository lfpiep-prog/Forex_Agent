import sys
import os

# Ensure current directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from execution.core.logger import get_logger

logger = get_logger("ConfigCheck")

def check_config():
    logger.info("Verifying Configuration...")
    try:
        from execution.core.config import settings
        logger.info("✅ Config imported successfully.")
        
        # Check critical fields - masked
        logger.info(f"IG Username: {settings.IG_USERNAME}")
        logger.info(f"IG Account Type: {settings.IG_ACC_TYPE}")
        
        # Check optional
        if settings.BRAVE_API_KEY:
            logger.info("✅ Brave API Key Presnet")
        else:
            logger.warning("⚠️ Brave API Key MISSING")
            
        logger.info("Configuration Verification PASSED.")
        
    except Exception as e:
        logger.error(f"❌ Configuration Verification FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_config()

"""
NEXUS-ON Windows Engine Service Wrapper
Runs as Windows Service or standalone application
"""
import sys
import os
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
log_dir = Path(os.getenv('DATA_DIR', 'C:/ProgramData/NEXUS-Engine')) / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'nexus.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    try:
        import uvicorn
        from nexus_supervisor.app import app
        
        port = int(os.getenv('PORT', '7100'))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"🚀 NEXUS Engine starting on {host}:{port}")
        logger.info(f"📂 Data directory: {os.getenv('DATA_DIR', 'default')}")
        logger.info(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'production')}")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            workers=1  # Single worker for Windows service
        )
    except Exception as e:
        logger.error(f"❌ Failed to start NEXUS Engine: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()

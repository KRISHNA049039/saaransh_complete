import logging as logger
import os
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_nirdesh_accessor():
    """Return NirdeshProjectAccessor if enabled, None otherwise"""
    
    # Check if Nirdesh integration is enabled
    if not os.getenv("ENABLE_NIRDESH", "false").lower() == "true":
        logger.info("Nirdesh integration is disabled")
        return None
    
    try:
        from app.accessors.nirdesh_project_accessor import NirdeshProjectAccessor
        
        logger.info("Initializing Nirdesh project accessor...")
        accessor = NirdeshProjectAccessor()
        logger.info("Nirdesh project accessor initialized successfully")
        return accessor
        
    except Exception as e:
        logger.error(f"Failed to initialize Nirdesh accessor: {e}")
        logger.warning("Continuing without Nirdesh integration")
        print(traceback.format_exc())
        return None

def get_asana_accessor():
    """Return AsanaAccessor if enabled, None otherwise"""
    
    # Check if Asana integration is enabled
    if not os.getenv("ENABLE_ASANA", "false").lower() == "true":
        logger.info("Asana integration is disabled")
        return None
    
    try:
        # First try to import the asana package itself
        import asana
        logger.info(f"Asana package imported successfully")
        
        # Then import our accessor
        from app.accessors.asana_accessor import AsanaAccessor
        
        logger.info("Initializing Asana accessor...")
        accessor = AsanaAccessor()
        
        # Check if access token is provided
        if not accessor.access_token:
            logger.warning("ASANA_ACCESS_TOKEN not provided - Asana integration disabled")
            return None
        
        # Check if client was initialized
        if not accessor.client:
            logger.warning("Asana client not initialized - Asana integration disabled")
            return None
        
        logger.info("Asana accessor initialized successfully")
        return accessor
        
    except ImportError as e:
        logger.error(f"Failed to import Asana dependencies: {e}")
        logger.warning("Make sure 'asana' package is installed: pip install asana")
        print(f"ImportError: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Asana accessor: {e}")
        logger.warning("Continuing without Asana integration")
        print(traceback.format_exc())
        return None
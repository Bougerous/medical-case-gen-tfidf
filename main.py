#!/usr/bin/env python3
"""Main entry point for the Medical Case Scenario Generator."""
import os
import sys
from loguru import logger

# Set environment variables for performance
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
from src.utils.logger import setup_logger
setup_logger()

logger.info("Starting Medical Case Scenario Generator")

if __name__ == "__main__":
    logger.info("Launching Streamlit interface")
    os.system("streamlit run src/cli/app.py --server.port=8503")
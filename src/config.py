"""
Configuration for the Medical Case Scenario Generator
"""
import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = os.path.join(BASE_DIR, "docs", "clean")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DB_DIR = os.path.join(BASE_DIR, "data", "chromadb")

# Create directories if they don't exist
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# LLM Configuration
DEFAULT_LLM_MODEL = "llama3.2:1b"  # Updated to an available model
OLLAMA_BASE_URL = "http://localhost:11434"

# Redis Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # Set this in production

# Vector DB Configuration
CHROMA_COLLECTION_NAME = "medical_knowledge"

# CLI Configuration
APP_NAME = "MedCaseGen"
APP_VERSION = "0.1.0"

# Difficulty Levels
DIFFICULTY_LEVELS = {
    1: "Medical Student",
    2: "Intern",
    3: "Post Graduate",
    4: "Expert"
}

# Case Types
CASE_TYPES = [
    "Outpatient",
    "Inpatient",
    "Emergency/Casualty",
    "ICU",
    "NICU",
    "PICU"
]

# Medical Specialties
MEDICAL_SPECIALTIES = [
    "Internal Medicine",
    "Cardiology",
    "Pulmonology",
    "Gastroenterology",
    "Neurology",
    "Nephrology",
    "Endocrinology",
    "Hematology",
    "Oncology",
    "Infectious Disease",
    "Rheumatology",
    "Emergency Medicine",
    "Critical Care",
    "Pediatrics"
]

# Structured data formats
MEDICINE_JSON_FORMAT = {
    "name": "",
    "dose": "",
    "route": "",
    "frequency": "",
    "duration": "",
    "start_date": "",
    "end_date": "",
    "special_instructions": ""
}

INVESTIGATION_JSON_FORMAT = {
    "name": "",
    "type": "",  # Lab, Imaging, Procedure
    "ordered_date": "",
    "results_date": "",
    "results": "",
    "interpretation": ""
}

VITALS_JSON_FORMAT = {
    "date_time": "",
    "temperature": "",
    "pulse": "",
    "respiratory_rate": "",
    "blood_pressure": "",
    "oxygen_saturation": "",
    "pain_score": ""
}

EXAMINATION_JSON_FORMAT = {
    "date_time": "",
    "system": "",
    "findings": "",
    "interpretation": ""
}
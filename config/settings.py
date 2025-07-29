import os
from typing import Dict, Any

# Application Configuration
APP_CONFIG = {
    "name": "AI-Powered Resume Analyser",
    "version": "1.0.0",
    "description": "Analyze and tailor resumes using AI",
    "author": "Your Name",
    "max_file_size": 10 * 1024 * 1024,  # 10MB in bytes
    "allowed_extensions": ["pdf", "docx", "txt"],
    "default_language": "en"
}

# Gemini API Configuration
GEMINI_CONFIG = {
    "model_name": "gemini-1.5-flash",  # Updated to current model name
    "generation_config": {
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 2048,
        "candidate_count": 1
    },
    "safety_settings": [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ],
    "rate_limit": {
        "requests_per_minute": 60,
        "requests_per_day": 1000
    }
}

# LangChain Configuration
LANGCHAIN_CONFIG = {
    "verbose": False,
    "temperature": 0.7,
    "max_tokens": 2048,
    "timeout": 30  # seconds
}

# File Processing Configuration
FILE_CONFIG = {
    "max_pages": 10,  # Maximum pages to process from PDF
    "encoding": "utf-8",
    "chunk_size": 1000,  # For large documents
    "overlap": 200,  # Overlap between chunks
    "supported_formats": {
        "pdf": {
            "mime_types": ["application/pdf"],
            "max_size": 10 * 1024 * 1024  # 10MB
        },
        "docx": {
            "mime_types": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
            "max_size": 5 * 1024 * 1024  # 5MB
        },
        "txt": {
            "mime_types": ["text/plain"],
            "max_size": 1 * 1024 * 1024  # 1MB
        }
    }
}

# UI Configuration
UI_CONFIG = {
    "theme": {
        "primary_color": "#1f77b4",
        "background_color": "#ffffff",
        "secondary_color": "#ff7f0e",
        "text_color": "#262730"
    },
    "layout": {
        "sidebar_width": 300,
        "main_width": "wide",
        "show_progress": True
    },
    "components": {
        "show_debug": False,
        "enable_caching": True,
        "auto_refresh": False
    }
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    "scoring": {
        "excellent_threshold": 85,
        "good_threshold": 70,
        "fair_threshold": 50
    },
    "keyword_matching": {
        "exact_match_weight": 1.0,
        "partial_match_weight": 0.7,
        "synonym_match_weight": 0.5,
        "case_sensitive": False
    },
    "resume_sections": [
        "contact_information",
        "professional_summary",
        "work_experience",
        "education",
        "skills",
        "certifications",
        "projects",
        "achievements"
    ],
    "job_analysis_fields": [
        "technical_skills",
        "soft_skills",
        "experience_level",
        "education_requirements",
        "responsibilities",
        "qualifications"
    ]
}

# Caching Configuration
CACHE_CONFIG = {
    "enabled": True,
    "ttl": 3600,  # 1 hour in seconds
    "max_size": 100,  # Maximum number of cached items
    "persist": False  # Whether to persist cache to disk
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "app.log",
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Security Configuration
SECURITY_CONFIG = {
    "max_upload_size": 10 * 1024 * 1024,  # 10MB
    "allowed_mime_types": [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    ],
    "scan_uploads": True,
    "sanitize_text": True
}

# Feature Flags
FEATURE_FLAGS = {
    "enable_pdf_upload": True,
    "enable_docx_upload": True,
    "enable_txt_upload": True,
    "enable_batch_processing": False,
    "enable_analytics": True,
    "enable_export": True,
    "enable_templates": True,
    "enable_suggestions": True
}

# API Endpoints (if needed for external services)
API_ENDPOINTS = {
    "gemini": "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
    "backup_service": None,
    "analytics": None
}

# Default Templates
DEFAULT_TEMPLATES = {
    "resume_sections": {
        "contact": "Contact Information",
        "summary": "Professional Summary",
        "experience": "Work Experience",
        "education": "Education",
        "skills": "Skills",
        "certifications": "Certifications",
        "projects": "Projects"
    },
    "output_formats": ["txt", "docx", "pdf"],
    "suggestion_categories": [
        "Keywords",
        "Experience",
        "Skills",
        "Education",
        "Formatting"
    ]
}

# Error Messages
ERROR_MESSAGES = {
    "file_too_large": "File size exceeds maximum limit of {max_size}MB",
    "invalid_format": "File format not supported. Please upload PDF, DOCX, or TXT files",
    "api_error": "Error connecting to AI service. Please try again later",
    "parsing_error": "Error parsing document. Please check file format",
    "analysis_error": "Error during analysis. Please try again",
    "no_text_found": "No text found in the uploaded document"
}

# Success Messages
SUCCESS_MESSAGES = {
    "file_uploaded": "File uploaded successfully",
    "analysis_complete": "Analysis completed successfully",
    "resume_generated": "Tailored resume generated successfully",
    "export_complete": "Export completed successfully"
}

def get_config(section: str) -> Dict[str, Any]:
    """
    Get configuration for a specific section
    
    Args:
        section: Configuration section name
        
    Returns:
        Configuration dictionary for the section
    """
    config_map = {
        "app": APP_CONFIG,
        "gemini": GEMINI_CONFIG,
        "langchain": LANGCHAIN_CONFIG,
        "file": FILE_CONFIG,
        "ui": UI_CONFIG,
        "analysis": ANALYSIS_CONFIG,
        "cache": CACHE_CONFIG,
        "logging": LOGGING_CONFIG,
        "security": SECURITY_CONFIG,
        "features": FEATURE_FLAGS,
        "api": API_ENDPOINTS,
        "templates": DEFAULT_TEMPLATES,
        "errors": ERROR_MESSAGES,
        "success": SUCCESS_MESSAGES
    }
    
    return config_map.get(section, {})

def is_feature_enabled(feature_name: str) -> bool:
    """
    Check if a feature is enabled
    
    Args:
        feature_name: Name of the feature to check
        
    Returns:
        True if feature is enabled, False otherwise
    """
    return FEATURE_FLAGS.get(feature_name, False)

def get_max_file_size(file_type: str) -> int:
    """
    Get maximum file size for a specific file type
    
    Args:
        file_type: File extension (pdf, docx, txt)
        
    Returns:
        Maximum file size in bytes
    """
    return FILE_CONFIG["supported_formats"].get(file_type, {}).get("max_size", 0)

def validate_environment():
    """
    Validate that all required environment variables are set
    
    Returns:
        List of missing environment variables
    """
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars
import os
import google.generativeai as genai
from typing import Dict, List, Optional
import json
import time
from config.settings import GEMINI_CONFIG
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    """Service class for Google Gemini API integration"""
    
    def __init__(self):
        """Initialize Gemini service with API key and configuration"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Try different model names (Google has been updating these)
        model_names_to_try = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "gemini-pro"
        ]
        
        self.model = None
        for model_name in model_names_to_try:
            try:
                self.model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=GEMINI_CONFIG['generation_config']
                )
                # Test the model with a simple query
                test_response = self.model.generate_content("Test")
                if test_response:
                    print(f"✅ Successfully initialized model: {model_name}")
                    break
            except Exception as e:
                print(f"❌ Failed to initialize {model_name}: {str(e)}")
                continue
        
        if not self.model:
            raise ValueError("Could not initialize any Gemini model. Please check your API key and available models.")
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1  # Minimum seconds between requests
    
    def _rate_limit(self):
        """Implement basic rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def generate_response(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Generate response from Gemini API with error handling and retries
        
        Args:
            prompt: The input prompt
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated response text or None if failed
        """
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                
                response = self.model.generate_content(prompt)
                
                if response.text:
                    return response.text.strip()
                else:
                    print(f"Empty response on attempt {attempt + 1}")
                    
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) * 2
                    time.sleep(wait_time)
                else:
                    print(f"Failed after {max_retries} attempts")
                    raise e
        
        return None
    
    def generate_structured_response(self, prompt: str, expected_format: str = "json") -> Optional[Dict]:
        """
        Generate structured response (JSON) from Gemini API
        
        Args:
            prompt: The input prompt
            expected_format: Expected response format
            
        Returns:
            Parsed JSON response or None if failed
        """
        try:
            # Add format instruction to prompt
            structured_prompt = f"{prompt}\n\nPlease respond in valid {expected_format.upper()} format only."
            
            response_text = self.generate_response(structured_prompt)
            
            if response_text:
                # Try to extract JSON from response
                return self._extract_json(response_text)
            
        except Exception as e:
            print(f"Error generating structured response: {str(e)}")
            
        return None
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from response text
        
        Args:
            text: Response text that may contain JSON
            
        Returns:
            Parsed JSON dict or None if parsing failed
        """
        try:
            # Try direct parsing first
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON within the text
            import re
            
            # Look for JSON-like patterns
            json_patterns = [
                r'\{.*\}',  # Single object
                r'\[.*\]',  # Array
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, text, re.DOTALL)
                for match in matches:
                    try:
                        return json.loads(match)
                    except json.JSONDecodeError:
                        continue
            
            print(f"Could not extract valid JSON from: {text[:200]}...")
            return None
    
    def analyze_job_description(self, job_text: str) -> Optional[Dict]:
        """
        Analyze job description to extract key requirements
        
        Args:
            job_text: Job description text
            
        Returns:
            Structured analysis of job requirements
        """
        from templates.prompts import JOB_ANALYSIS_PROMPT
        
        prompt = JOB_ANALYSIS_PROMPT.format(job_description=job_text)
        return self.generate_structured_response(prompt)
    
    def analyze_resume(self, resume_text: str, job_requirements: Dict) -> Optional[Dict]:
        """
        Analyze resume against job requirements
        
        Args:
            resume_text: Resume text content
            job_requirements: Extracted job requirements
            
        Returns:
            Structured analysis of resume match
        """
        from templates.prompts import RESUME_ANALYSIS_PROMPT
        
        prompt = RESUME_ANALYSIS_PROMPT.format(
            resume_text=resume_text,
            job_requirements=json.dumps(job_requirements, indent=2)
        )
        return self.generate_structured_response(prompt)
    
    def generate_tailored_resume(self, resume_text: str, job_requirements: Dict, analysis: Dict) -> Optional[str]:
        """
        Generate tailored resume based on analysis
        
        Args:
            resume_text: Original resume text
            job_requirements: Job requirements analysis
            analysis: Resume analysis results
            
        Returns:
            Tailored resume text
        """
        from templates.prompts import RESUME_TAILORING_PROMPT
        
        prompt = RESUME_TAILORING_PROMPT.format(
            original_resume=resume_text,
            job_requirements=json.dumps(job_requirements, indent=2),
            analysis=json.dumps(analysis, indent=2)
        )
        return self.generate_response(prompt)
    
    def get_suggestions(self, analysis_results: Dict) -> Optional[List[str]]:
        """
        Generate improvement suggestions based on analysis
        
        Args:
            analysis_results: Complete analysis results
            
        Returns:
            List of improvement suggestions
        """
        from templates.prompts import SUGGESTIONS_PROMPT
        
        prompt = SUGGESTIONS_PROMPT.format(
            analysis_results=json.dumps(analysis_results, indent=2)
        )
        
        response = self.generate_response(prompt)
        
        if response:
            # Parse suggestions from response
            suggestions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    suggestions.append(line.lstrip('-•* '))
            
            return suggestions if suggestions else [response]
        
        return None
    
    def check_api_status(self) -> bool:
        """
        Check if Gemini API is accessible
        
        Returns:
            True if API is working, False otherwise
        """
        try:
            test_prompt = "Say 'API is working' if you can read this."
            response = self.generate_response(test_prompt)
            return response is not None and "API is working" in response
        except Exception:
            return False
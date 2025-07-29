from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseOutputParser
from typing import Dict, List, Optional
import json
import os
from templates.prompts import *
from dotenv import load_dotenv

load_dotenv()

class JSONOutputParser(BaseOutputParser):
    """Custom output parser for JSON responses"""
    
    def parse(self, text: str) -> Dict:
        """Parse JSON from LLM output"""
        try:
            # Clean the text
            cleaned_text = text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            # Parse JSON
            return json.loads(cleaned_text.strip())
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Text: {text[:200]}...")
            # Return a basic structure if parsing fails
            return {"error": "Failed to parse JSON", "raw_text": text}

class LangChainService:
    """Service class for LangChain integration with Gemini"""
    
    def __init__(self):
        """Initialize LangChain service"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Initialize Gemini LLM through LangChain
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Updated to current model name
            google_api_key=self.api_key,
            temperature=0.7,
            max_output_tokens=2048
        )
        
        # Initialize output parser
        self.json_parser = JSONOutputParser()
        
        # Initialize prompt templates
        self._setup_prompt_templates()
        
        # Initialize chains
        self._setup_chains()
    
    def _setup_prompt_templates(self):
        """Setup all prompt templates"""
        
        # Job analysis prompt template
        self.job_analysis_template = PromptTemplate(
            input_variables=["job_description"],
            template=JOB_ANALYSIS_PROMPT
        )
        
        # Resume analysis prompt template
        self.resume_analysis_template = PromptTemplate(
            input_variables=["resume_text", "job_analysis"],
            template=RESUME_ANALYSIS_PROMPT
        )
        
        # Resume tailoring prompt template
        self.resume_tailoring_template = PromptTemplate(
            input_variables=["original_resume", "job_requirements", "analysis"],
            template=RESUME_TAILORING_PROMPT
        )
        
        # Suggestions prompt template
        self.suggestions_template = PromptTemplate(
            input_variables=["analysis_results"],
            template=SUGGESTIONS_PROMPT
        )
        
        # Keyword extraction prompt template
        self.keyword_extraction_template = PromptTemplate(
            input_variables=["text", "context"],
            template=KEYWORD_EXTRACTION_PROMPT
        )
    
    def _setup_chains(self):
        """Setup LangChain chains"""
        
        # Job analysis chain
        self.job_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.job_analysis_template,
            output_key="job_analysis",
            verbose=False
        )
        
        # Resume analysis chain
        self.resume_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.resume_analysis_template,
            output_key="resume_analysis",
            verbose=False
        )
        
        # Resume tailoring chain
        self.resume_tailoring_chain = LLMChain(
            llm=self.llm,
            prompt=self.resume_tailoring_template,
            output_key="tailored_resume",
            verbose=False
        )
        
        # Suggestions chain
        self.suggestions_chain = LLMChain(
            llm=self.llm,
            prompt=self.suggestions_template,
            output_key="suggestions",
            verbose=False
        )
        
        # Note: Removed SequentialChain due to input/output key mismatch
        # Using individual chains instead for better control
    
    def analyze_job_description(self, job_description: str) -> Dict:
        """
        Analyze job description to extract key requirements
        
        Args:
            job_description: Job description text
            
        Returns:
            Structured analysis of job requirements
        """
        try:
            result = self.job_analysis_chain.invoke(job_description=job_description)
            parsed_result = self.json_parser.parse(result)
            
            # Ensure required fields exist
            default_structure = {
                "technical_skills": [],
                "soft_skills": [],
                "experience_level": "Not specified",
                "education": "Not specified",
                "key_responsibilities": [],
                "required_qualifications": [],
                "preferred_qualifications": [],
                "company_culture": "",
                "key_skills": []
            }
            
            # Merge with defaults
            for key, default_value in default_structure.items():
                if key not in parsed_result:
                    parsed_result[key] = default_value
            
            # Combine all skills into key_skills if not present
            if not parsed_result["key_skills"]:
                parsed_result["key_skills"] = (
                    parsed_result["technical_skills"] + 
                    parsed_result["soft_skills"]
                )
            
            return parsed_result
            
        except Exception as e:
            print(f"Error analyzing job description: {e}")
            return self._get_default_job_analysis()
    
    def analyze_resume(self, resume_text: str, job_analysis: Dict) -> Dict:
        """
        Analyze resume against job requirements
        
        Args:
            resume_text: Resume text content
            job_analysis: Extracted job requirements
            
        Returns:
            Structured analysis of resume match
        """
        try:
            result = self.resume_analysis_chain.invoke(
                resume_text=resume_text,
                job_analysis=json.dumps(job_analysis, indent=2)
            )
            parsed_result = self.json_parser.parse(result)
            
            # Ensure required fields exist
            default_structure = {
                "match_score": 0,
                "matched_keywords": [],
                "missing_keywords": [],
                "strengths": [],
                "gaps": [],
                "recommendations": [],
                "experience_match": "",
                "education_match": "",
                "skill_coverage": 0
            }
            
            # Merge with defaults
            for key, default_value in default_structure.items():
                if key not in parsed_result:
                    parsed_result[key] = default_value
            
            # Calculate match score if not provided
            if parsed_result["match_score"] == 0 and parsed_result["matched_keywords"]:
                total_keywords = len(parsed_result["matched_keywords"]) + len(parsed_result["missing_keywords"])
                if total_keywords > 0:
                    parsed_result["match_score"] = int((len(parsed_result["matched_keywords"]) / total_keywords) * 100)
            
            return parsed_result
            
        except Exception as e:
            print(f"Error analyzing resume: {e}")
            return self._get_default_resume_analysis()
    
    def generate_tailored_resume(self, resume_text: str, job_analysis: Dict, analysis: Dict) -> str:
        """
        Generate tailored resume based on analysis
        
        Args:
            resume_text: Original resume text
            job_analysis: Job requirements analysis
            analysis: Resume analysis results
            
        Returns:
            Tailored resume text
        """
        try:
            result = self.resume_tailoring_chain.invoke(
                original_resume=resume_text,
                job_requirements=json.dumps(job_analysis, indent=2),
                analysis=json.dumps(analysis, indent=2)
            )
            
            return result.strip()
            
        except Exception as e:
            print(f"Error generating tailored resume: {e}")
            return f"Error generating tailored resume: {str(e)}\n\nOriginal resume:\n{resume_text}"
    
    def generate_suggestions(self, analysis_results: Dict) -> List[str]:
        """
        Generate improvement suggestions based on analysis
        
        Args:
            analysis_results: Complete analysis results
            
        Returns:
            List of improvement suggestions
        """
        try:
            result = self.suggestions_chain.invoke(
                analysis_results=json.dumps(analysis_results, indent=2)
            )
            
            # Parse suggestions from response
            suggestions = []
            for line in result.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    suggestions.append(line.lstrip('-•* '))
                elif line and len(line) > 10:  # Include substantial lines
                    suggestions.append(line)
            
            return suggestions if suggestions else [result]
            
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return ["Error generating suggestions. Please review the analysis manually."]
    
    def extract_keywords(self, text: str, context: str = "general") -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Text to extract keywords from
            context: Context for keyword extraction
            
        Returns:
            List of extracted keywords
        """
        try:
            result = self.keyword_extraction_template.format(text=text, context=context)
            response = self.llm.predict(result)
            
            # Parse keywords from response
            keywords = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    keywords.append(line.lstrip('-•* '))
            
            return keywords
            
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def run_complete_analysis(self, job_description: str, resume_text: str) -> Dict:
        """
        Run complete analysis pipeline
        
        Args:
            job_description: Job description text
            resume_text: Resume text
            
        Returns:
            Complete analysis results
        """
        try:
            # Run job analysis
            job_analysis = self.analyze_job_description(job_description)
            
            # Run resume analysis
            resume_analysis = self.analyze_resume(resume_text, job_analysis)
            
            # Generate tailored resume
            tailored_resume = self.generate_tailored_resume(resume_text, job_analysis, resume_analysis)
            
            # Generate suggestions
            suggestions = self.generate_suggestions({
                'job_analysis': job_analysis,
                'resume_analysis': resume_analysis
            })
            
            return {
                'job_analysis': job_analysis,
                'resume_analysis': resume_analysis,
                'tailored_resume': tailored_resume,
                'suggestions': suggestions
            }
            
        except Exception as e:
            print(f"Error in complete analysis: {e}")
            return self._get_default_complete_analysis()
    
    def _get_default_job_analysis(self) -> Dict:
        """Return default job analysis structure"""
        return {
            "technical_skills": ["Python", "Communication", "Problem Solving"],
            "soft_skills": ["Teamwork", "Leadership"],
            "experience_level": "Mid-level",
            "education": "Bachelor's degree preferred",
            "key_responsibilities": ["Develop software solutions"],
            "required_qualifications": ["3+ years experience"],
            "preferred_qualifications": ["Advanced degree"],
            "company_culture": "Collaborative environment",
            "key_skills": ["Python", "Communication", "Problem Solving", "Teamwork", "Leadership"]
        }
    
    def _get_default_resume_analysis(self) -> Dict:
        """Return default resume analysis structure"""
        return {
            "match_score": 50,
            "matched_keywords": ["Python", "Communication"],
            "missing_keywords": ["Leadership", "Problem Solving"],
            "strengths": ["Strong technical background"],
            "gaps": ["Missing leadership experience"],
            "recommendations": ["Add more leadership examples"],
            "experience_match": "Partially matches",
            "education_match": "Meets requirements",
            "skill_coverage": 50
        }
    
    def _get_default_complete_analysis(self) -> Dict:
        """Return default complete analysis structure"""
        return {
            'job_analysis': self._get_default_job_analysis(),
            'resume_analysis': self._get_default_resume_analysis(),
            'tailored_resume': "Unable to generate tailored resume due to analysis error.",
            'suggestions': ["Review job requirements carefully", "Highlight relevant experience"]
        }
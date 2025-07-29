import re
import string
from typing import Dict, List, Set, Tuple
from collections import Counter
import streamlit as st
from config.settings import ANALYSIS_CONFIG

class ResumeProcessor:
    """Process and analyze resume content"""
    
    def __init__(self):
        """Initialize resume processor with configuration"""
        self.config = ANALYSIS_CONFIG
        self.scoring_thresholds = self.config["scoring"]
        self.keyword_weights = self.config["keyword_matching"]
        
        # Common stop words for keyword filtering
        self.stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an'
        }
        
        # Common synonyms for skill matching
        self.skill_synonyms = {
            'javascript': ['js', 'javascript', 'ecmascript'],
            'python': ['python', 'py'],
            'artificial intelligence': ['ai', 'artificial intelligence', 'machine learning', 'ml'],
            'machine learning': ['ml', 'machine learning', 'artificial intelligence', 'ai'],
            'database': ['db', 'database', 'databases'],
            'leadership': ['leadership', 'lead', 'leading', 'manage', 'management'],
            'communication': ['communication', 'communicate', 'communicating'],
            'project management': ['project management', 'pm', 'project manager'],
            'software development': ['software development', 'development', 'programming'],
            'web development': ['web development', 'web dev', 'frontend', 'backend']
        }
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for processing
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep alphanumeric and basic punctuation
        text = re.sub(r'[^\w\s\-\.\,\;\:\!\?]', ' ', text)
        
        return text
    
    def extract_keywords(self, text: str, min_length: int = 2) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Text to extract keywords from
            min_length: Minimum keyword length
            
        Returns:
            List of extracted keywords
        """
        if not text:
            return []
        
        # Clean and normalize text
        cleaned_text = self.clean_text(text.lower())
        
        # Split into words and phrases
        words = re.findall(r'\b\w+\b', cleaned_text)
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if len(word) >= min_length and word not in self.stop_words
        ]
        
        # Also extract phrases (2-3 words)
        phrases = self._extract_phrases(cleaned_text)
        
        # Combine and deduplicate
        all_keywords = list(set(keywords + phrases))
        
        return all_keywords
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases from text"""
        phrases = []
        
        # Common technical phrases patterns
        phrase_patterns = [
            r'\b(?:machine learning|artificial intelligence|data science|software engineering)\b',
            r'\b(?:project management|team leadership|customer service)\b',
            r'\b(?:web development|mobile development|database management)\b',
            r'\b(?:quality assurance|business analysis|system administration)\b'
        ]
        
        for pattern in phrase_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            phrases.extend([match.lower() for match in matches])
        
        return phrases
    
    def match_keywords(self, resume_keywords: List[str], job_keywords: List[str]) -> Dict[str, List[str]]:
        """
        Match keywords between resume and job description
        
        Args:
            resume_keywords: Keywords extracted from resume
            job_keywords: Keywords extracted from job description
            
        Returns:
            Dictionary with matched and missing keywords
        """
        # Normalize keywords
        resume_set = {kw.lower().strip() for kw in resume_keywords}
        job_set = {kw.lower().strip() for kw in job_keywords}
        
        # Find exact matches
        exact_matches = resume_set.intersection(job_set)
        
        # Find partial matches using synonyms
        partial_matches = set()
        for job_kw in job_set:
            if job_kw not in exact_matches:
                for resume_kw in resume_set:
                    if self._are_synonyms(job_kw, resume_kw):
                        partial_matches.add(job_kw)
                        break
        
        # All matched keywords
        matched_keywords = exact_matches.union(partial_matches)
        
        # Missing keywords
        missing_keywords = job_set - matched_keywords
        
        return {
            'matched': list(matched_keywords),
            'missing': list(missing_keywords),
            'exact_matches': list(exact_matches),
            'partial_matches': list(partial_matches)
        }
    
    def _are_synonyms(self, word1: str, word2: str) -> bool:
        """Check if two words are synonyms"""
        # Direct match
        if word1 == word2:
            return True
        
        # Check in synonym dictionary
        for key, synonyms in self.skill_synonyms.items():
            if word1 in synonyms and word2 in synonyms:
                return True
        
        # Check if one word contains the other (for variations)
        if len(word1) > 3 and len(word2) > 3:
            if word1 in word2 or word2 in word1:
                return True
        
        return False
    
    def calculate_match_score(self, matched_keywords: List[str], total_job_keywords: List[str]) -> int:
        """
        Calculate overall match score as percentage
        
        Args:
            matched_keywords: List of matched keywords
            total_job_keywords: List of all job keywords
            
        Returns:
            Match score as percentage (0-100)
        """
        if not total_job_keywords:
            return 0
        
        match_ratio = len(matched_keywords) / len(total_job_keywords)
        return min(100, int(match_ratio * 100))
    
    def analyze_resume_sections(self, resume_text: str) -> Dict[str, str]:
        """
        Identify and extract different sections of resume
        
        Args:
            resume_text: Full resume text
            
        Returns:
            Dictionary with identified sections
        """
        sections = {}
        
        # Common section headers
        section_patterns = {
            'contact': r'(?:contact|personal|address|phone|email)',
            'summary': r'(?:summary|profile|objective|about)',
            'experience': r'(?:experience|employment|work|career|professional)',
            'education': r'(?:education|academic|degree|university|college)',
            'skills': r'(?:skills|technical|competencies|abilities)',
            'certifications': r'(?:certifications?|licenses?|credentials)',
            'projects': r'(?:projects?|portfolio)',
            'achievements': r'(?:achievements?|awards?|honors?|accomplishments?)'
        }
        
        lines = resume_text.split('\n')
        current_section = 'other'
        section_content = {section: [] for section in section_patterns.keys()}
        section_content['other'] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            line_lower = line.lower()
            found_section = False
            
            for section, pattern in section_patterns.items():
                if re.search(pattern, line_lower) and len(line.split()) <= 3:
                    current_section = section
                    found_section = True
                    break
            
            if not found_section:
                section_content[current_section].append(line)
        
        # Convert lists to strings
        for section, content in section_content.items():
            sections[section] = '\n'.join(content)
        
        return sections
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract technical and soft skills from text
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of identified skills
        """
        skills = []
        
        # Common technical skills patterns
        tech_skills = [
            r'\b(?:python|java|javascript|c\+\+|c#|ruby|php|go|rust|swift)\b',
            r'\b(?:react|angular|vue|node\.?js|express|django|flask)\b',
            r'\b(?:sql|mysql|postgresql|mongodb|redis|elasticsearch)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins)\b',
            r'\b(?:git|github|gitlab|bitbucket|svn)\b',
            r'\b(?:html|css|sass|less|bootstrap|tailwind)\b',
            r'\b(?:machine learning|artificial intelligence|data science|nlp)\b',
            r'\b(?:agile|scrum|kanban|devops|ci/cd)\b'
        ]
        
        # Extract technical skills
        for pattern in tech_skills:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.extend(matches)
        
        # Common soft skills
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'analytical thinking', 'creativity', 'adaptability', 'time management',
            'project management', 'customer service', 'negotiation', 'presentation'
        ]
        
        # Extract soft skills
        text_lower = text.lower()
        for skill in soft_skills:
            if skill in text_lower:
                skills.append(skill)
        
        return list(set(skills))  # Remove duplicates
    
    def get_keyword_frequency(self, text: str, keywords: List[str]) -> Dict[str, int]:
        """
        Get frequency of keywords in text
        
        Args:
            text: Text to analyze
            keywords: Keywords to count
            
        Returns:
            Dictionary with keyword frequencies
        """
        text_lower = text.lower()
        frequencies = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Count exact word matches
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            matches = re.findall(pattern, text_lower)
            frequencies[keyword] = len(matches)
        
        return frequencies
    
    def suggest_improvements(self, analysis_results: Dict) -> List[str]:
        """
        Generate improvement suggestions based on analysis
        
        Args:
            analysis_results: Results from resume analysis
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        missing_keywords = analysis_results.get('missing_keywords', [])
        match_score = analysis_results.get('match_score', 0)
        
        # Score-based suggestions
        if match_score < self.scoring_thresholds['fair_threshold']:
            suggestions.append("Consider significantly restructuring your resume to better align with job requirements")
        elif match_score < self.scoring_thresholds['good_threshold']:
            suggestions.append("Add more relevant keywords and experiences to improve job match")
        
        # Missing keywords suggestions
        if missing_keywords:
            high_priority_keywords = missing_keywords[:5]  # Top 5 missing
            suggestions.append(f"Include these important keywords: {', '.join(high_priority_keywords)}")
        
        # Section-specific suggestions
        if 'skills' in analysis_results:
            skills_section = analysis_results['skills']
            if len(skills_section.split()) < 10:
                suggestions.append("Expand your skills section with more relevant technical and soft skills")
        
        if 'experience' in analysis_results:
            exp_section = analysis_results['experience']
            if 'quantified' not in exp_section.lower() and 'achieved' not in exp_section.lower():
                suggestions.append("Add quantified achievements and specific results to your experience")
        
        return suggestions
    
    def format_tailored_content(self, original_text: str, improvements: Dict) -> str:
        """
        Format tailored resume content
        
        Args:
            original_text: Original resume text
            improvements: Suggested improvements and additions
            
        Returns:
            Formatted tailored content
        """
        # This is a basic implementation - can be enhanced based on needs
        sections = self.analyze_resume_sections(original_text)
        
        formatted_content = []
        
        # Add enhanced sections
        for section_name, content in sections.items():
            if content.strip():
                # Add section header
                formatted_content.append(f"\n{section_name.upper()}\n" + "="*20)
                
                # Add enhanced content
                if section_name in improvements:
                    enhanced_content = improvements[section_name]
                    formatted_content.append(enhanced_content)
                else:
                    formatted_content.append(content)
        
        return "\n".join(formatted_content)
# Prompt templates for AI-powered resume analysis

JOB_ANALYSIS_PROMPT = """
Analyze the following job description and extract key information in JSON format.

Job Description:
{job_description}

Extract the following information and respond ONLY with valid JSON:

{{
    "technical_skills": ["list of technical skills required"],
    "soft_skills": ["list of soft skills required"],
    "experience_level": "entry/mid/senior level description",
    "education": "education requirements",
    "key_responsibilities": ["main job responsibilities"],
    "required_qualifications": ["must-have qualifications"],
    "preferred_qualifications": ["nice-to-have qualifications"],
    "company_culture": "description of company culture/values",
    "key_skills": ["combined list of all important keywords and skills"]
}}

Focus on extracting specific, actionable keywords that would appear in a resume. Be comprehensive but precise.
"""

RESUME_ANALYSIS_PROMPT = """
Analyze the following resume against the job requirements and provide a detailed comparison in JSON format.

Resume Text:
{resume_text}

Job Requirements:
{job_analysis}

Analyze the resume and respond ONLY with valid JSON:

{{
    "match_score": 85,
    "matched_keywords": ["list of keywords from job requirements found in resume"],
    "missing_keywords": ["list of important keywords from job requirements NOT found in resume"],
    "strengths": ["specific strengths of this resume for this job"],
    "gaps": ["specific areas where resume falls short of job requirements"],
    "recommendations": ["specific actionable recommendations to improve match"],
    "experience_match": "description of how experience level matches",
    "education_match": "description of how education matches",
    "skill_coverage": 75
}}

Be thorough in keyword matching. Look for synonyms and related terms. The match_score should be a percentage (0-100) representing overall job fit.
"""

RESUME_TAILORING_PROMPT = """
Create a tailored version of the resume that better matches the job requirements. Maintain the original person's experience and qualifications while optimizing presentation for the target role.

Original Resume:
{original_resume}

Job Requirements:
{job_requirements}

Resume Analysis:
{analysis}

Guidelines for tailoring:
1. Keep all factual information accurate - do not fabricate experience
2. Reorder sections to highlight most relevant experience first
3. Adjust language to match job description keywords where appropriate
4. Emphasize relevant skills and accomplishments
5. Add or expand on experiences that align with job requirements
6. Use action verbs and quantifiable achievements
7. Maintain professional formatting and readability

Provide the complete tailored resume maintaining the original structure but optimized for this specific job:
"""

SUGGESTIONS_PROMPT = """
Based on the resume analysis results, provide specific, actionable suggestions for improving the resume to better match the job requirements.

Analysis Results:
{analysis_results}

Provide clear, prioritized suggestions in the following format:
- [High Priority] Specific action to take
- [Medium Priority] Another specific action
- [Low Priority] Additional improvement

Focus on:
1. Missing keywords that should be incorporated
2. Skills that should be emphasized more
3. Experience that should be reframed
4. Formatting or structure improvements
5. Additional achievements to highlight

Make suggestions specific and actionable, not generic advice.
"""

KEYWORD_EXTRACTION_PROMPT = """
Extract the most important keywords and phrases from the following text in the context of {context}.

Text:
{text}

Extract keywords that would be relevant for:
- Skills and technologies
- Job titles and roles
- Industry terminology
- Qualifications and certifications
- Action verbs and achievements

Return as a simple list, one keyword per line, starting with a dash (-).
"""

SKILLS_MATCHING_PROMPT = """
Compare the skills mentioned in the resume with those required for the job. Identify matches, gaps, and opportunities for better alignment.

Resume Skills:
{resume_skills}

Job Required Skills:
{job_skills}

Provide analysis in JSON format:
{{
    "exact_matches": ["skills that match exactly"],
    "close_matches": ["skills that are similar or related"],
    "missing_critical": ["important job skills not found in resume"],
    "resume_extras": ["resume skills not mentioned in job but potentially valuable"],
    "recommendations": ["how to better align skills presentation"]
}}
"""

EXPERIENCE_ANALYSIS_PROMPT = """
Analyze how well the candidate's experience aligns with the job requirements.

Candidate Experience:
{candidate_experience}

Job Requirements:
{job_requirements}

Provide detailed analysis focusing on:
1. Years of relevant experience
2. Industry alignment
3. Role progression
4. Specific accomplishments that match job needs
5. Leadership and impact examples
6. Technical depth in required areas

Return analysis as structured text with clear sections.
"""

ATS_OPTIMIZATION_PROMPT = """
Optimize the resume content for Applicant Tracking Systems (ATS) while maintaining readability.

Original Content:
{content}

Job Keywords:
{keywords}

Optimize by:
1. Including relevant keywords naturally
2. Using standard section headers
3. Avoiding graphics, tables, or complex formatting
4. Using industry-standard terminology
5. Ensuring keyword density is appropriate
6. Maintaining natural language flow

Return the optimized content:
"""

COVER_LETTER_PROMPT = """
Generate a tailored cover letter based on the resume and job description.

Resume Summary:
{resume_summary}

Job Description:
{job_description}

Company Information:
{company_info}

Create a compelling cover letter that:
1. Opens with enthusiasm for the specific role
2. Highlights 2-3 most relevant achievements from resume
3. Demonstrates knowledge of the company
4. Shows how candidate can add value
5. Closes with a strong call to action

Keep it concise (3-4 paragraphs) and personalized.
"""

SALARY_NEGOTIATION_PROMPT = """
Provide salary negotiation guidance based on the job analysis and candidate profile.

Job Analysis:
{job_analysis}

Candidate Profile:
{candidate_profile}

Market Data Context:
{market_context}

Provide guidance on:
1. Salary range expectations for this role
2. Key value propositions to emphasize
3. Negotiation timing and approach
4. Non-salary benefits to consider
5. Preparation strategies

Format as actionable advice with specific talking points.
"""
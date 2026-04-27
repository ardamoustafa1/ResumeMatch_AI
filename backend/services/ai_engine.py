import os
import json
import logging
import asyncio
from typing import Dict, Any

import httpx
from groq import AsyncGroq, APIError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from backend.models.schemas import (
    AnalysisRequest,
    MatchResult,
    OutreachMessages,
    ProfileImprovements,
    FullAnalysisResult,
)

logger = logging.getLogger(__name__)

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")

# Initialize Groq client if key is available
groq_client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- Exceptions ---
class AnalysisTimeoutError(Exception):
    """Raised when the AI analysis takes longer than the allowed timeout."""
    pass


# --- Prompts ---
MATCH_PROMPT_SYSTEM = """
You are an expert technical recruiter and ATS system. 
Analyze the provided CV against the provided Job Description (JD).
You must output ONLY valid JSON matching this exact structure:
{
  "score": <integer from 0 to 100>,
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "improvement_suggestions": ["suggestion1", "suggestion2"]
}
"""

OUTREACH_PROMPT_SYSTEM = """
You are an elite executive recruiter known for writing highly personalized, non-cringe, and effective outreach messages.
Based on the candidate's CV and the Job Description, write messages to recruit them.
You must output ONLY valid JSON matching this exact structure:
{
  "dm_first_contact": "<3-4 sentences, warm, specific, human>",
  "dm_follow_up": "<Brief day 7 follow up message>",
  "connection_note": "<Max 280 characters LinkedIn connection note>"
}
"""

PROFILE_IMPROVEMENTS_PROMPT_SYSTEM = """
You are an expert personal branding coach for tech professionals.
Analyze the provided CV and suggest LinkedIn profile improvements.
You must output ONLY valid JSON matching this exact structure:
{
  "headline_before": "<Extract their current or implied headline>",
  "headline_after": "<Keyword optimized, max 120 chars>",
  "about_section": "<4-5 sentences, achievement-focused, first-person>"
}
"""

# --- Helper Methods ---

async def _call_groq(system_prompt: str, user_prompt: str) -> str:
    """Calls Groq API."""
    if not groq_client:
        raise APIError("GROQ_API_KEY is not set.")
    
    response = await groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content


async def _call_ollama(system_prompt: str, user_prompt: str) -> str:
    """Calls local Ollama as a fallback."""
    logger.info(f"Using Ollama fallback with model {OLLAMA_MODEL}")
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        }
        response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]


@retry(
    stop=stop_after_attempt(2), 
    wait=wait_fixed(2), 
    retry=retry_if_exception_type(json.JSONDecodeError),
    reraise=True
)
async def _generate_json(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Primary orchestrator for AI generation. 
    Tries Groq first, falls back to Ollama on APIError or missing key.
    Retries once if JSONDecodeError occurs.
    """
    raw_response = ""
    try:
        raw_response = await _call_groq(system_prompt, user_prompt)
    except Exception as e:
        logger.warning(f"Groq failed ({e}). Falling back to Ollama.")
        raw_response = await _call_ollama(system_prompt, user_prompt)
        
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from AI. Raw response: {raw_response}")
        # When tenacity retries, we can append a strict reminder to the prompt
        system_prompt += "\\nCRITICAL: Output ONLY valid JSON. No markdown formatting."
        raise e


# --- AI Pipeline Functions ---

async def analyze_cv_jd_match(cv: str, jd: str) -> MatchResult:
    """
    Analyzes CV against JD to determine match score and missing/matched skills.
    """
    user_prompt = f"CV:\\n{cv}\\n\\nJob Description:\\n{jd}"
    
    try:
        # Wrap in 30s timeout
        data = await asyncio.wait_for(
            _generate_json(MATCH_PROMPT_SYSTEM, user_prompt), 
            timeout=30.0
        )
        return MatchResult(**data)
    except asyncio.TimeoutError:
        raise AnalysisTimeoutError("analyze_cv_jd_match timed out after 30 seconds.")


async def generate_outreach_messages(
    cv: str, 
    jd: str, 
    company: str, 
    recruiter_name: str, 
    match_result: MatchResult
) -> OutreachMessages:
    """
    Generates personalized outreach messages.
    """
    context = (
        f"Recruiter Name: {recruiter_name}\\n"
        f"Company: {company}\\n"
        f"Match Score: {match_result.score}\\n"
        f"Missing Skills to avoid mentioning: {', '.join(match_result.missing_skills)}\\n\\n"
        f"CV:\\n{cv}\\n\\nJob Description:\\n{jd}"
    )
    
    try:
        data = await asyncio.wait_for(
            _generate_json(OUTREACH_PROMPT_SYSTEM, context), 
            timeout=30.0
        )
        return OutreachMessages(**data)
    except asyncio.TimeoutError:
        raise AnalysisTimeoutError("generate_outreach_messages timed out after 30 seconds.")


async def generate_profile_improvements(cv: str, jd: str) -> ProfileImprovements:
    """
    Suggests LinkedIn profile improvements based on CV and targeted JD.
    """
    user_prompt = f"Target Job Description:\\n{jd}\\n\\nCandidate CV:\\n{cv}"
    
    try:
        data = await asyncio.wait_for(
            _generate_json(PROFILE_IMPROVEMENTS_PROMPT_SYSTEM, user_prompt), 
            timeout=30.0
        )
        return ProfileImprovements(**data)
    except asyncio.TimeoutError:
        raise AnalysisTimeoutError("generate_profile_improvements timed out after 30 seconds.")


async def run_full_pipeline(request: AnalysisRequest) -> FullAnalysisResult:
    """
    Orchestrates the entire AI analysis pipeline, handling partial failures.
    """
    result = FullAnalysisResult()
    
    # Step 1: Match Analysis (Critical Path)
    try:
        logger.info("Starting CV/JD match analysis...")
        result.match_result = await analyze_cv_jd_match(request.cv_text, request.jd_text)
    except Exception as e:
        logger.error(f"Failed to generate match result: {e}")
        # If match fails, we can't reliably generate outreach messages, but we can still try profile improvements
        pass
        
    # Step 2: Outreach Messages (Requires MatchResult to be effective)
    if result.match_result:
        try:
            logger.info("Starting outreach message generation...")
            result.outreach_messages = await generate_outreach_messages(
                cv=request.cv_text,
                jd=request.jd_text,
                company=request.company or "our company",
                recruiter_name=request.recruiter_name or "a recruiter",
                match_result=result.match_result
            )
        except Exception as e:
            logger.error(f"Failed to generate outreach messages: {e}")

    # Step 3: Profile Improvements
    try:
        logger.info("Starting profile improvements generation...")
        result.profile_improvements = await generate_profile_improvements(
            request.cv_text, request.jd_text
        )
    except Exception as e:
        logger.error(f"Failed to generate profile improvements: {e}")

    return result

#!/usr/bin/env python3
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path so we can import backend
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.services.ai_engine import analyze_cv_jd_match  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SAMPLE_CV = """
Alex Doe
Senior Software Engineer
Experience:
- 5 years building Python APIs with FastAPI and PostgreSQL.
- Deployed microservices using Docker and Kubernetes.
- Optimized Redis caching layers to reduce latency by 40%.
- Strong background in cloud infrastructure (AWS) and CI/CD pipelines.
"""

SAMPLE_JD = """
Backend Engineer (Python)
Requirements:
- Strong proficiency in Python and async frameworks (FastAPI preferred).
- Experience with relational databases (PostgreSQL) and NoSQL/Caching (Redis).
- Familiarity with containerization (Docker) and orchestration (Kubernetes) is a plus.
- Knowledge of Go or Rust is highly desirable.
- Experience with GCP or AWS.
"""


async def evaluate(iterations: int = 3):
    logger.info(f"Starting evaluation of CV/JD match score (iterations: {iterations})")

    # Check what providers we have
    groq_key = os.getenv("GROQ_API_KEY")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    if not groq_key:
        logger.warning(
            f"GROQ_API_KEY is not set. Will rely on Ollama fallback at {ollama_url}."
        )

    scores = []

    for i in range(iterations):
        logger.info(f"--- Iteration {i + 1} ---")
        try:
            result = await analyze_cv_jd_match(cv=SAMPLE_CV, jd=SAMPLE_JD)
            scores.append(result.score)
            logger.info(f"Score: {result.score}")
            logger.info(f"Matched Skills: {', '.join(result.matched_skills)}")
            logger.info(f"Missing Skills: {', '.join(result.missing_skills)}")
            logger.info("Improvement Suggestions:")
            for sug in result.improvement_suggestions:
                logger.info(f" - {sug}")
        except Exception as e:
            logger.error(f"Iteration {i + 1} failed: {e}")

    if scores:
        avg_score = sum(scores) / len(scores)
        variance = max(scores) - min(scores)
        logger.info("=== Evaluation Summary ===")
        logger.info(f"Total Runs: {len(scores)}")
        logger.info(f"Average Score: {avg_score:.1f}")
        logger.info(f"Score Variance (Max - Min): {variance}")

        if variance > 10:
            logger.warning(
                "High variance detected. The LLM might be hallucinating or the prompt is too ambiguous."
            )
        else:
            logger.info("Consistency is good.")
    else:
        logger.error("All iterations failed. Could not compute summary.")


if __name__ == "__main__":
    asyncio.run(evaluate())

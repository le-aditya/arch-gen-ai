"""LLM-only architecture judgment (PRD section 17B) -- no ML model involved."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from app.services.llm_service import get_provider  # noqa: E402


def predict_llm_only(description: str) -> str:
    provider = get_provider()
    return provider.judge_architecture(description)

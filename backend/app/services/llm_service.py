"""Natural-language requirement extraction. Provider is replaceable behind LLMProvider."""
import json
import os
import re
from abc import ABC, abstractmethod

from pydantic import ValidationError

from app.schemas.schemas import Requirements

DOMAIN_KEYWORDS = {
    "food_delivery": ["food", "restaurant", "delivery", "meal", "cuisine"],
    "e_commerce": ["shop", "store", "e-commerce", "ecommerce", "cart", "checkout", "product catalog"],
    "social_media": ["social", "feed", "post", "follow", "friend", "profile"],
    "fintech": ["bank", "payment", "wallet", "transfer", "loan", "finance", "invoice"],
    "healthtech": ["health", "patient", "doctor", "hospital", "appointment", "medical"],
    "edtech": ["course", "student", "learning", "class", "teacher", "quiz"],
    "logistics": ["delivery", "fleet", "tracking", "shipment", "route", "driver"],
    "gaming": ["game", "player", "multiplayer", "leaderboard", "match"],
    "media_streaming": ["stream", "video", "music", "watch", "playlist"],
    "booking_platform": ["book", "reservation", "appointment", "ticket", "schedule"],
    "marketplace": ["marketplace", "buyer", "seller", "vendor", "listing"],
    "iot_platform": ["sensor", "device", "iot", "telemetry"],
    "analytics_dashboard": ["analytics", "dashboard", "report", "metrics", "insight"],
}

ACTOR_KEYWORDS = {
    "customer": ["customer", "user", "buyer", "client"],
    "admin": ["admin", "manager", "operator"],
    "restaurant": ["restaurant", "vendor", "seller", "merchant"],
    "delivery_partner": ["delivery", "driver", "courier"],
    "doctor": ["doctor", "physician"],
    "patient": ["patient"],
    "teacher": ["teacher", "instructor"],
    "student": ["student", "learner"],
}

MODULE_KEYWORDS = {
    "registration": ["sign up", "register", "onboarding", "account"],
    "authentication": ["login", "auth", "sign in"],
    "browsing": ["browse", "search", "catalog", "listing"],
    "ordering": ["order", "purchase", "cart", "checkout"],
    "payment": ["payment", "pay", "billing", "invoice"],
    "tracking": ["track", "tracking", "live location", "status update"],
    "notifications": ["notify", "notification", "alert", "sms", "email"],
    "messaging": ["chat", "message", "messaging"],
    "reviews": ["review", "rating", "feedback"],
    "analytics": ["analytics", "dashboard", "report"],
}

INTEGRATION_KEYWORDS = {
    "maps": ["map", "location", "gps", "geolocation"],
    "payment_gateway": ["payment", "stripe", "razorpay", "paypal", "gateway"],
    "sms": ["sms", "text message"],
    "email": ["email"],
    "push_notifications": ["push notification"],
    "cloud_storage": ["storage", "upload", "file", "image", "video"],
}


class LLMProvider(ABC):
    @abstractmethod
    def extract_requirements(self, description: str) -> Requirements:
        raise NotImplementedError

    @abstractmethod
    def judge_architecture(self, description: str) -> str:
        """LLM-only architecture judgment, used by the four-way experiment (PRD section 17B)."""
        raise NotImplementedError


def _match_keywords(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    matches = []
    for label, keywords in keyword_map.items():
        if any(kw in text for kw in keywords):
            matches.append(label)
    return matches


class MockProvider(LLMProvider):
    """Deterministic keyword-based extraction. No network calls."""

    def extract_requirements(self, description: str) -> Requirements:
        text = description.lower()

        domain_matches = _match_keywords(text, DOMAIN_KEYWORDS)
        domain = domain_matches[0] if domain_matches else "productivity_tool"

        actors = _match_keywords(text, ACTOR_KEYWORDS) or ["customer"]
        modules = _match_keywords(text, MODULE_KEYWORDS) or ["registration", "browsing"]
        integrations = _match_keywords(text, INTEGRATION_KEYWORDS)

        real_time = bool(re.search(r"real[\s-]?time|live\s+tracking|instant", text))
        payment = "payment" in modules or bool(re.search(r"pay|purchase|checkout|billing", text))

        complexity_signal = len(modules) + len(integrations)
        if complexity_signal >= 6:
            data_complexity = "high"
        elif complexity_signal >= 3:
            data_complexity = "medium"
        else:
            data_complexity = "low"

        return Requirements(
            domain=domain,
            actors=actors,
            modules=modules,
            real_time=real_time,
            payment=payment,
            external_integrations=integrations,
            data_complexity=data_complexity,
        )

    def judge_architecture(self, description: str) -> str:
        text = description.lower()
        scale_words = ["million", "nationwide", "national", "global", "large scale", "enterprise"]
        small_words = ["mvp", "prototype", "hackathon", "small team", "solo", "weekend"]

        if any(w in text for w in scale_words):
            return "Microservices"
        if any(w in text for w in small_words):
            return "Serverless"
        return "Monolith"


class GeminiProvider(LLMProvider):
    """Calls Google Gemini for structured requirement extraction.

    Lazily imports google.generativeai so the mock path never requires it installed
    or configured. Falls back to raising LLMExtractionError on malformed output;
    callers should catch this and fall back to MockProvider rather than hard-failing.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-flash-latest"):
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self._genai = genai
        self._model = genai.GenerativeModel(model_name)

    def extract_requirements(self, description: str) -> Requirements:
        prompt = f"""Extract structured software requirements from this application description.
Return ONLY valid JSON matching this exact schema, no markdown fences, no commentary:
{{
  "domain": "string, e.g. food_delivery",
  "actors": ["string", ...],
  "modules": ["string", ...],
  "real_time": true/false,
  "payment": true/false,
  "external_integrations": ["string", ...],
  "data_complexity": "low" | "medium" | "high"
}}

Description: {description}"""

        response = self._model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()

        try:
            data = json.loads(raw)
            return Requirements(**data)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise LLMExtractionError(f"Gemini returned invalid JSON: {exc}") from exc

    def judge_architecture(self, description: str) -> str:
        prompt = (
            "Which software architecture style best fits this application: "
            "Monolith, Microservices, or Serverless? "
            f"Description: {description}\n"
            "Respond with exactly one word: Monolith, Microservices, or Serverless."
        )
        response = self._model.generate_content(prompt)
        text = response.text.strip()
        for label in ("Microservices", "Serverless", "Monolith"):
            if label.lower() in text.lower():
                return label
        return "Monolith"


class LLMExtractionError(Exception):
    pass


def get_provider() -> LLMProvider:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            return GeminiProvider(api_key=api_key)
        except Exception:
            return MockProvider()
    return MockProvider()


def extract_requirements_safe(description: str) -> Requirements:
    """Tries the configured provider; falls back to the mock provider on any failure
    (network error, malformed JSON after retry) rather than hard-failing the pipeline."""
    provider = get_provider()
    try:
        return provider.extract_requirements(description)
    except Exception:
        if isinstance(provider, MockProvider):
            raise
        return MockProvider().extract_requirements(description)

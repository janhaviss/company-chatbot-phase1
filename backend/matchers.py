import re
from knowledge_base import KNOWLEDGE_BASE


def preprocess_text(text: str) -> str:
    """
    Normalize user input before matching.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s.-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def keyword_matches(question: str, keywords: list[str]) -> list[str]:
    """
    Find which keywords from an intent appear in the user's question.
    """
    question = preprocess_text(question)

    matched = []

    for keyword in keywords:
        keyword = preprocess_text(keyword)

        # Phrase matching
        if keyword in question:
            matched.append(keyword)

    return matched


def calculate_score(question: str, keywords: list[str]) -> int:
    """
    Calculate how strongly an intent matches the user's question.
    """
    matched_keywords = keyword_matches(question, keywords)

    score = 0

    for keyword in matched_keywords:

        # Give more weight to multi-word phrases
        if " " in keyword:
            score += 3
        else:
            score += 1

    return score


def find_intent(question: str):
    """
    Find the best matching intent from the knowledge base.
    """

    question = preprocess_text(question)

    best_intent = None
    best_score = 0
    best_matches = []

    for intent, data in KNOWLEDGE_BASE.items():

        score = calculate_score(
            question,
            data["keywords"]
        )

        if score > best_score:
            best_score = score
            best_intent = intent
            best_matches = keyword_matches(
                question,
                data["keywords"]
            )

    # Nothing matched
    if best_intent is None:
        return {
            "intent": None,
            "confidence": 0.0,
            "matched_keywords": [],
            "answer": None
        }

    # Simple confidence calculation
    total_keywords = len(
        KNOWLEDGE_BASE[best_intent]["keywords"]
    )

    confidence = min(
        best_score / max(total_keywords, 1),
        1.0
    )

    return {
        "intent": best_intent,
        "confidence": round(confidence, 2),
        "matched_keywords": best_matches,
        "answer": KNOWLEDGE_BASE[best_intent]["answer"]
    }
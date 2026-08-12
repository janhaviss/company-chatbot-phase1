from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

from knowledge_base import KNOWLEDGE_BASE
from matchers import find_intent
from ai_service import ask_ai


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="Company AI Assistant",
    description=(
        "Hybrid company assistant using knowledge base, "
        "intent matching, and AI fallback"
    ),
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Configuration
# =========================================================

# The knowledge-base answer is used only when the matcher
# is sufficiently confident.

KB_CONFIDENCE_THRESHOLD = 0.70


# =========================================================
# Request / Response Models
# =========================================================

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    intent: Optional[str]
    confidence: float
    matched_keywords: List[str]
    answer: str
    source: str
    needs_contact: bool = False


class MenuOption(BaseModel):
    question_id: str
    question: str


class ContactRequest(BaseModel):
    email: EmailStr
    question: str


# =========================================================
# Root Endpoint
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Company AI Assistant is running.",
        "docs": "/docs"
    }


# =========================================================
# Chatbot Menu
# =========================================================

@app.get("/menu", response_model=List[MenuOption])
def get_menu():
    """
    Return example questions that can be displayed
    as clickable options in the frontend.
    """

    menu = []

    for intent, data in KNOWLEDGE_BASE.items():

        menu.append({
            "question_id": intent,
            "question": data["questions"][0]
        })

    return menu


# =========================================================
# Chat Endpoint
# =========================================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    question = request.question.strip()

    # -----------------------------------------------------
    # Basic validation
    # -----------------------------------------------------

    if not question:

        return {
            "question": question,
            "intent": None,
            "confidence": 0.0,
            "matched_keywords": [],
            "answer": "Please enter a question.",
            "source": "validation",
            "needs_contact": False
        }

    # -----------------------------------------------------
    # STEP 1: Knowledge Base / Keyword Matching
    # -----------------------------------------------------

    result = find_intent(question)

    intent = result.get("intent")
    confidence = result.get("confidence", 0.0)
    matched_keywords = result.get("matched_keywords", [])
    answer = result.get("answer")

    # -----------------------------------------------------
    # STEP 2: Strong KB Match
    # -----------------------------------------------------

    if (
        intent is not None
        and confidence >= KB_CONFIDENCE_THRESHOLD
        and answer
    ):

        return {
            "question": question,
            "intent": intent,
            "confidence": confidence,
            "matched_keywords": matched_keywords,
            "answer": answer,
            "source": "knowledge_base",
            "needs_contact": False
        }

    # -----------------------------------------------------
    # STEP 3: AI FALLBACK
    # -----------------------------------------------------

    ai_answer = ask_ai(question)

    # -----------------------------------------------------
    # STEP 4: AI Cannot Answer
    # -----------------------------------------------------

    if ai_answer == "CONTACT_TEAM":

        return {
            "question": question,
            "intent": "contact_team",
            "confidence": confidence,
            "matched_keywords": matched_keywords,
            "answer": (
                "I don't have enough information to answer "
                "that accurately. Please provide your email "
                "so our team can get back to you."
            ),
            "source": "contact_team",
            "needs_contact": True
        }

    # -----------------------------------------------------
    # STEP 5: AI Successfully Answered
    # -----------------------------------------------------

    return {
        "question": question,
        "intent": "ai_fallback",
        "confidence": confidence,
        "matched_keywords": matched_keywords,
        "answer": ai_answer,
        "source": "ai",
        "needs_contact": False
    }


# =========================================================
# Contact / Lead Endpoint
# =========================================================

@app.post("/contact")
def contact_team(request: ContactRequest):

    print("New enquiry received")
    print("Email:", request.email)
    print("Question:", request.question)

    return {
        "message": (
            "Thank you. Our team will get back to you "
            "at the provided email address."
        )
    }
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

from knowledge_base import KNOWLEDGE_BASE
from matchers import find_intent
from ai_service import ask_ai


app = FastAPI(
    title="Company AI Assistant",
    description="Hybrid company assistant using knowledge base, intent matching, and AI fallback",
    version="1.0.0"
)


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

# A match must reach this confidence before we trust the knowledge base answer.
KB_CONFIDENCE_THRESHOLD = 0.70

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

@app.get("/")
def root():
    return {
        "message": "Company AI Assistant is running.",
        "docs": "/docs"
    }


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

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    result = find_intent(request.question)

    intent = result.get("intent")
    confidence = result.get("confidence", 0.0)
    matched_keywords = result.get("matched_keywords", [])
    answer = result.get("answer")

    if (
        intent is not None
        and confidence >= KB_CONFIDENCE_THRESHOLD
        and answer
    ):

        return {
            "question": request.question,
            "intent": intent,
            "confidence": confidence,
            "matched_keywords": matched_keywords,
            "answer": answer,
            "source": "knowledge_base",
            "needs_contact": False
        }

    ai_answer = ask_ai(request.question)
    if ai_answer == "CONTACT_TEAM":

        return {
            "question": request.question,
            "intent": "contact_team",
            "confidence": 0.0,
            "matched_keywords": matched_keywords,
            "answer": (
                "I don't have enough information to answer "
                "that accurately. Please provide your email "
                "so our team can get back to you."
            ),
            "source": "contact_team",
            "needs_contact": True
        }

    return {
        "question": request.question,
        "intent": "ai_fallback",
        "confidence": 0.0,
        "matched_keywords": matched_keywords,
        "answer": ai_answer,
        "source": "ai",
        "needs_contact": False
    }



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
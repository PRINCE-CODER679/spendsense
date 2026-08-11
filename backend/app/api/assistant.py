import json
import urllib.request
import urllib.error
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.config import settings
from app.services.financial_summary import build_financial_context
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    suggested_followups: List[str]
    source: str  # "gemini", "openai", or "fallback_engine"


def generate_fallback_response(user_msg: str, financial_context: str) -> str:
    """Smart fallback response generator when no LLM API key is set or on API errors."""
    msg_lower = user_msg.lower()

    if any(k in msg_lower for k in ["budget", "overspend", "over-budget", "limit", "track"]):
        return (
            "Here is your current **Budget Breakdown** based on live data:\n\n"
            f"{financial_context}\n\n"
            "💡 **Tip:** Review categories marked as OVER_BUDGET or NEAR_LIMIT to avoid overspending before month-end."
        )

    elif any(k in msg_lower for k in ["top", "category", "categories", "where", "most"]):
        return (
            "Here are your **Top Spending Categories**:\n\n"
            f"{financial_context}\n\n"
            "💡 **Tip:** Reallocating even 10-15% of discretionary category spending to savings can significantly boost your savings rate!"
        )

    elif any(k in msg_lower for k in ["forecast", "project", "projection", "end of month", "future", "predict"]):
        return (
            "Here is your **Spending Forecast & Projections**:\n\n"
            f"{financial_context}\n\n"
            "💡 **Tip:** Projections calculate daily spending velocity to estimate end-of-month totals."
        )

    elif any(k in msg_lower for k in ["anomaly", "anomalies", "unusual", "spike", "strange", "flag"]):
        return (
            "Here are your **Recent Spending Anomalies & Alerts**:\n\n"
            f"{financial_context}\n\n"
            "💡 **Tip:** High severity alerts highlight daily spikes or unusually large individual transactions."
        )

    elif any(k in msg_lower for k in ["savings", "income", "expense", "rate", "summary", "how am i doing"]):
        return (
            "Here is your overall **Financial Health Summary**:\n\n"
            f"{financial_context}\n\n"
            "💡 **Tip:** Maintaining a savings rate above 20% is recommended for healthy financial growth."
        )

    else:
        return (
            f"Hello! I am your **SpendSense AI Financial Assistant**. Here is your current real-time financial snapshot:\n\n"
            f"{financial_context}\n\n"
            "You can ask me questions like:\n"
            "• *Am I staying within my budget?*\n"
            "• *Where am I spending the most money?*\n"
            "• *Were any unusual transactions flagged recently?*\n"
            "• *What is my projected end-of-month spending?*"
        )


async def call_gemini_api(api_key: str, system_context: str, user_msg: str, history: List[ChatMessage]) -> str:
    """Calls Gemini REST API directly using standard urllib."""
    model = settings.LLM_MODEL or "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    prompt = (
        "You are SpendSense AI Financial Assistant, a friendly, concise, and expert personal finance advisor.\n"
        "Analyze the user's real-time financial context below and provide tailored, actionable advice.\n"
        "Use Markdown formatting (bolding, bullet points, numbers) for clear readability. Always reference exact numbers where relevant.\n\n"
        f"{system_context}\n\n"
        f"User Question: {user_msg}"
    )

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 800
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    with urllib.request.urlopen(req, timeout=12) as response:
        resp_data = json.loads(response.read().decode('utf-8'))
        candidates = resp_data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "")
    
    raise ValueError("No valid response text returned from Gemini API")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    POST /api/assistant/chat
    Process user finance query using LLM (Gemini/OpenAI) or smart rule engine fallback for authenticated user.
    """
    try:
        financial_context = await build_financial_context(user_id=str(current_user.id))

        # Default follow-up suggestions
        suggested_followups = [
            "Am I staying within my budget?",
            "What are my top 5 expense categories?",
            "Were any unusual transactions detected?",
            "What is my end-of-month forecast?"
        ]

        # 1. Try Gemini if GEMINI_API_KEY is configured
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                reply = await call_gemini_api(
                    settings.GEMINI_API_KEY.strip(),
                    financial_context,
                    request.message,
                    request.history or []
                )
                return ChatResponse(
                    reply=reply,
                    suggested_followups=suggested_followups,
                    source="gemini"
                )
            except Exception as e:
                print(f"Warning: Gemini API call failed, falling back to rule engine: {e}")

        # 2. Rule engine fallback
        fallback_reply = generate_fallback_response(request.message, financial_context)
        return ChatResponse(
            reply=fallback_reply,
            suggested_followups=suggested_followups,
            source="fallback_engine"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assistant processing error: {str(e)}")

# Company AI Assistant

A hybrid AI chatbot for a company website using **FastAPI, React, keyword/intent matching, a company knowledge base, and OpenRouter AI fallback**.

## Features

- Answers common company-related questions from a knowledge base
- Keyword and intent-based matching
- Confidence-based response selection
- AI fallback for questions that don't match the knowledge base
- Contact-team fallback when the AI cannot answer safely
- Suggested questions through the `/menu` endpoint
- React-based chat interface

## Tech Stack

- **Frontend:** React
- **Backend:** FastAPI
- **AI:** OpenRouter
- **Language:** Python
- **Data:** Python-based knowledge base

## How It Works

```text
User Question
      ↓
Intent / Keyword Matcher
      ↓
High confidence?
   ↙          ↘
 Yes           No
  ↓             ↓
Knowledge     AI
  Base       Fallback
                ↓
          Contact Team
          if necessary
```

Common questions are answered directly from the knowledge base, so they do not require an AI API call.

## Project Structure

```text
backend/
├── main.py
├── matchers.py
├── knowledge_base.py
├── ai_service.py
├── requirements.txt
└── .env

frontend/
└── React application
```

## Setup

### Backend

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Run the FastAPI server:

```bash
uvicorn main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
npm install
npm run dev
```

The React development server normally runs at:

```text
http://localhost:5173
```

## API Endpoints

### `GET /`

Checks that the backend is running.

### `GET /menu`

Returns suggested questions for the chatbot.

### `POST /chat`

Main chatbot endpoint.

Example:

```json
{
  "question": "What services do you provide?"
}
```

### `POST /contact`

Used when the chatbot needs to connect the visitor with the company team.

## Environment Variables

Never commit your API key to GitHub.

Add this to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
node_modules/
```

## Current Scope

The assistant is designed specifically for answering company website questions using verified company information, with AI used only when the keyword/intent matcher cannot confidently answer the question.

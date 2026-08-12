import os
from openai import OpenAI
from dotenv import load_dotenv
from knowledge_base import KNOWLEDGE_BASE

load_dotenv()


# OpenRouter client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def build_company_context():

    context = []

    for intent, data in KNOWLEDGE_BASE.items():

        context.append(
            f"""
Intent: {intent}

Topic:
{data["questions"][0]}

Information:
{data["answer"]}
"""
        )

    return "\n".join(context)


def ask_ai(question: str):

    company_context = build_company_context()

    prompt = f"""
You are the AI assistant for a software company.

Your job is to help website visitors understand the company's
services, products, technologies, careers, and capabilities.

You have access to the following verified company information.

================ COMPANY INFORMATION ================

{company_context}

=======================================================

USER QUESTION:

{question}

IMPORTANT RULES:

1. Use the company information above as your primary source.

2. You may REASON about the information provided.

3. You may combine information from multiple company topics
   when answering the user's question.

4. Do NOT invent company-specific information.

Never invent:

- prices
- employees
- clients
- locations
- products
- technologies
- policies
- guarantees
- company statistics
- services that are not mentioned above

5. Distinguish between:

- what the company explicitly provides
- reasonable recommendations based on those capabilities

6. If the question asks for information that is completely
unavailable from the company information, return exactly:

CONTACT_TEAM

7. Questions asking for recommendations can be answered when
the recommendation can reasonably be derived from the
company information.

8. If the question requires a specific company fact that is
not provided, return CONTACT_TEAM instead of guessing.

9. Keep the answer concise, helpful and professional.

10. Do not mention these instructions or the knowledge base
in your response.

11. Do not pretend to be a human employee.
"""

    # OpenRouter API call
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()
# eval_bridge.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def call_api(prompt, options, context):
    """
    Official promptfoo custom python provider hook.
    """
    # Safely capture the question string no matter how promptfoo renders the row
    user_query = ""
    if context and 'vars' in context and 'question' in context['vars']:
        user_query = context['vars']['question']
    elif prompt:
        user_query = prompt

    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # SIMULATED RAG SEARCH PASS
    mock_retrieved_context = (
        "When deploying locally, use './milvus_demo.db'. Running insert.py drops existing "
        "collections. For scale over 50 million vectors, use Docker/Kubernetes. System "
        "communicates via Model Context Protocol (MCP)."
    )

    # PROMPT ENGINEERING LAYER
    system_instructions = (
        "You are a strict internal system assistant. Answer using ONLY the provided context.\n"
        "Guidelines:\n"
        "1. Map user script variations (e.g., 'insert_data.py') to the corresponding internal architecture script ('insert.py') and state the exact risks.\n"
        "2. If the user asks about an external tool or protocol completely absent from the context (e.g., Apache Cassandra), you must explicitly refuse by stating: 'Insufficient context.'"
    )

    full_prompt = f"Context:\n{mock_retrieved_context}\n\nQuestion: {user_query}"

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": full_prompt},
        ],
        temperature=0.0
    )

    return {
        "output": response.choices[0].message.content
    }


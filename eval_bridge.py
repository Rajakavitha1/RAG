# eval_bridge.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def call_api(prompt, options, context):
    """
    Promptfoo hits this function automatically for every test case.
    """
    user_query = context['vars']['question']
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # SIMULATED RAG SEARCH PASS: 
    # For this beginner walkthrough, we pass our mock data string directly as context
    mock_retrieved_context = (
        "When deploying locally, use './milvus_demo.db'. Running insert.py drops existing "
        "collections. For scale over 50 million vectors, use Docker/Kubernetes. System "
        "communicates via Model Context Protocol (MCP)."
    )

    # PROMPT ENGINEERING LAYER:
    # We tell the model exactly how to behave.
    system_instructions = (
        "You are a strict internal system assistant. Answer using ONLY the provided context. "
        "If the answer cannot be found in the context, state: 'Insufficient context.'"
    )

    full_prompt = f"Context:\n{mock_retrieved_context}\n\nQuestion: {user_query}"

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": full_prompt},
        ],
        temperature=0.0 # 0.0 makes the model factual and consistent
    )

    return {
        "output": response.choices[0].message.content
    }


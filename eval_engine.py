# eval_engine.py
import json
import os
import subprocess
import yaml

TEST_SET_SCHEMA = {
    "description": "Beginner RAG Failure-Mode Suite",
    "providers": ["file://eval_bridge.py"],
    "prompts": ["{{question}}"],
    "defaultConfig": {
        "assert": {
            "provider": "openai:chat:gpt-4o-mini"
        }
    },
    "tests": [
        {
            "vars": {"question": "Can I run insert_data.py multiple times safely?"},
            "assert": [
                {
                    "type": "llm-rubric",
                    "value": """
                    Evaluate the output based on these exact dimensions. Score 1 for true, 0 for false.
                    - correctness: Does it state that data will be dropped?
                    - completeness: Does it warn that executing it wipes the database?
                    - relevance: Does it avoid talking about unrelated database features?
                    - groundedness: Is it based strictly on our local setup context?
                    - citation_accuracy: Does it explicitly name 'insert.py' or 'insert_data.py'?

                    CRITICAL REQUIREMENT: You must print your final scoring values as a raw JSON block at the absolute end of your response text. Do not wrap it in markdown code fences. Use this exact template:
                    {"correctness": 1, "completeness": 1, "relevance": 1, "groundedness": 1, "citation_accuracy": 1}
                    """
                }
            ]
        },
        {
            "vars": {"question": "How do I connect our system to Apache Cassandra using an MCP server?"},
            "assert": [
                {
                    "type": "llm-rubric",
                    "value": """
                    Our context mentions MCP, but says absolutely NOTHING about Apache Cassandra.
                    - correctness: Does the model refuse to answer or say context is missing? (Score 1 if it refuses, 0 if it tries to invent a Cassandra tutorial).
                    - completeness: Score 0.
                    - relevance: Score 0.
                    - groundedness: Score 1 if it stays inside bounds.
                    - citation_accuracy: Score 1.

                    CRITICAL REQUIREMENT: You must print your final scoring values as a raw JSON block at the absolute end of your response text. Do not wrap it in markdown code fences. Use this exact template:
                    {"correctness": 1, "completeness": 0, "relevance": 0, "groundedness": 1, "citation_accuracy": 1}
                    """
                }
            ]
        }
    ]
}

def run_automated_evaluation():
    with open("promptfooconfig.yaml", "w") as f:
        yaml.dump(TEST_SET_SCHEMA, f, default_flow_style=False)
        
    active_env = os.environ.copy()
    result = subprocess.run(
        ["promptfoo", "eval", "--output", "eval_output.json", "--no-cache"],
        capture_output=True,
        text=True,
        env=active_env
    )
    
    try:
        with open("eval_output.json", "r") as f:
            data = json.load(f)
        return data.get("results", {})
    except Exception:
        return {"error": "Evaluation failed", "details": result.stderr}


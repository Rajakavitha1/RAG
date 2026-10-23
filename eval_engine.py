# eval_engine.py
import json
import os
import subprocess
import yaml  # <--- CRITICAL: Make sure this import is present at the very top!

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

                    CRITICAL REQUIREMENT: You must print your final scoring values as a raw JSON block at the absolute end of your response:
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
                    - correctness: Does the model refuse to answer or say context is missing? (Score 1 if it refuses, 0 if it tries to guess)
                    - completeness: Score 0.
                    - relevance: Score 0.
                    - groundedness: Score 1 if it stays inside bounds.
                    - citation_accuracy: Score 1.

                    CRITICAL REQUIREMENT: You must print your final scoring values as a raw JSON block at the absolute end of your response:
                    {"correctness": 1, "completeness": 0, "relevance": 0, "groundedness": 1, "citation_accuracy": 1}
                    """
                }
            ]
        },
        {
            "vars": {"question": "Can I run 60 million vectors on a standard local configuration?"},
            "assert": [
                {
                    "type": "llm-rubric",
                    "value": """
                    Our context strictly dictates production architecture limits for high vector volumes.
                    - correctness: Does the model explicitly state that local debugging configurations CANNOT handle this volume? (Score 1 if yes, 0 if no)
                    - completeness: Does it provide the exact step-by-step setup guides for Kubernetes deployment? (Score 1 if yes, 0 if it only mentions the keyword 'Kubernetes' without giving full documentation steps)
                    - relevance: Score 1.
                    - groundedness: Score 1.
                    - citation_accuracy: Score 1.

                    CRITICAL REQUIREMENT: You must print your final scoring values as a raw JSON block at the absolute end of your response:
                    {"correctness": 1, "completeness": 1, "relevance": 1, "groundedness": 1, "citation_accuracy": 1}
                    """
                }
            ]
        }
    ]
}

def run_automated_evaluation():
    print("🚀 Initializing Promptfoo evaluation suite...")
    
    config_filename = "promptfoo_temp_config.yaml"
    with open(config_filename, "w") as f:
        yaml.dump(TEST_SET_SCHEMA, f, default_flow_style=False)
        
    print(f"📦 Config written to {config_filename}. Running assertions...")
    
    try:
        # Executes evaluation, captures matrix details, and exports telemetry logs
        result = subprocess.run(
            ["npx", "promptfoo", "eval", "-c", config_filename, "-o", "eval_output.json", "--no-cache"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("⚠️ Evaluation complete with test failures (expected outcome):")
        print(e.stdout)
        print(e.stderr)
    finally:
        if os.path.exists(config_filename):
            os.remove(config_filename)

if __name__ == "__main__":
    run_automated_evaluation()


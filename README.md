

# Multi-Dimensional RAG Evaluation Sandbox

A failure-mode-driven evaluation sandbox for benchmarking Retrieval-Augmented Generation (RAG) applications. The project explores how technical documentation can be used as a knowledge source for generating and evaluating model responses across five dimensions: correctness, completeness, relevance, groundedness, and citation accuracy.

The sandbox integrates Promptfoo, Milvus Lite, and OpenAI to support retrieval, response generation, and structured evaluation. Its goal is to make RAG failure modes easier to identify, analyze, and address through repeatable evaluation workflows.

> **Project status:** This README describes the intended workflow and current project structure. Claims about implementation, scoring behavior, and evaluation reliability should be confirmed against the source code and execution results before the project is described as production-ready.

<img width="1260" height="753" alt="Matrix" src="https://github.com/user-attachments/assets/894e7e16-3fc4-4feb-bedf-38e59679959a" />

## System Architecture

The intended workflow separates the interactive user interface from the programmatic evaluation pipeline. A dedicated bridge coordinates retrieval and model inference, while the evaluation layer assesses generated responses against a defined rubric.

```text
                    User Query
                        |
                        v
                 eval_bridge.py
                        |
                        v
                 Milvus Lite
                Context Retrieval
                        |
                        v
                 OpenAI Model
               Response Generation
                        |
                        v
              Evaluation and Scoring
                        |
                        v
                 Promptfoo / Judge
                        |
                        v
              Structured Evaluation Results
                        |
                        v
                    app.py
                 Results Display
```

The exact execution order and integration points depend on the implementation in `eval_bridge.py`, `eval_engine.py`, and `app.py`. Verify these relationships against the code before treating this diagram as a definitive representation of runtime behavior.

### Architectural Components

- **Knowledge base:** Provides technical documentation for retrieval and response grounding.
- **Vector database:** Milvus Lite stores indexed document chunks and supports similarity-based retrieval.
- **Generation model:** OpenAI generates responses using the query and any retrieved context supplied by the pipeline.
- **Evaluation layer:** Applies the configured evaluation criteria to model responses.
- **Evaluation interface:** Streamlit provides an interface for triggering workflows and inspecting results, where implemented.

## Repository Structure

The project contains five core files.

| File | Component | Responsibility |
|---|---|---|
| `app.py` | Streamlit interface | Provides the interactive application interface for running evaluations and viewing results, as implemented. |
| `eval_engine.py` | Evaluation orchestration | Defines or coordinates test cases, evaluation criteria, and scoring logic. |
| `eval_bridge.py` | Programmatic pipeline bridge | Connects the evaluation workflow with retrieval and model inference without requiring the Streamlit interface. |
| `insert_data.py` | Data ingestion utility | Processes source content and loads document data into the local vector database. |
| `knowledge.txt` | Knowledge base | Contains the technical content used as the source for retrieval and response generation. |

## Prerequisites

Before setting up the project, ensure the following are available:

* Python 3: Required to run the application and its Python dependencies.

* Node.js and npm: Required to install and run Promptfoo.

* OpenAI API key: Required for model inference if the project uses the OpenAI API. The key must have access to the configured model and sufficient API quota.

* Terminal with virtual environment support: Required to create and activate an isolated Python environment.

Note: Promptfoo must be installed and available on your system if the evaluation workflow invokes its CLI. Verify its role in the application code before treating it as a mandatory runtime dependency.

Milvus Lite runs as an embedded vector database, so a separate Milvus server installation is generally not required.

## Installation and Environment Setup

### 1. Create and activate a virtual environment

From the project root, run:

```bash
python3 -m venv env
source env/bin/activate
```

This isolates the project's Python dependencies from the system Python installation.

On Windows, activate the environment using:

```powershell
env\Scripts\Activate.ps1
```

### 2. Install Promptfoo and Python dependencies

Install Promptfoo:

```bash
npm install -g promptfoo@latest
```

Install the Python packages:

```bash
python3 -m pip install \
  python-dotenv \
  pandas \
  pyyaml \
  streamlit \
  "pymilvus[milvus_lite]" \
  openai
```

These commands install the dependencies listed for this project. They do not, by themselves, verify compatibility or guarantee that the complete evaluation pipeline runs successfully.

### 3. Configure environment variables

Create a `.env` file in the project root:

```dotenv
OPENAI_API_KEY=your_openai_api_key
MILVUS_ENDPOINT=./milvus_demo.db
COLLECTION_NAME=my_rag_collection
```

Replace the API key placeholder with your own key. Confirm that the variable names and expected values match the application's configuration code.

**Security considerations:**

- Never commit `.env` or API credentials to version control.
- Add `.env` and other sensitive local artifacts to `.gitignore`.
- Do not share logs or evaluation output containing secrets.

## Data Ingestion and Execution

Run the following commands from the project root with the virtual environment activated.

1. Ingest the knowledge base

Run the ingestion script:

```bash
python3 insert_data.py
```

This is intended to prepare the knowledge base for retrieval by processing and inserting its content into the local vector database.

Verify that the script completes successfully and that the expected collection and document records are available before running evaluations.

2. Clear previous evaluation artifacts (optional)

To remove the specified local artifacts before a fresh run:

```bash
rm -f eval_output.json promptfooconfig.yaml
```

This command deletes those files if they exist. Back them up first if they contain evaluation results or configuration you need to retain.

**Important:** Confirm how `app.py` and `eval_engine.py` generate or consume these files before deleting them. The command does not automatically clear the Milvus database or all historical evaluation data.

3. Launch the Streamlit application

Start the interface:

```bash
streamlit run app.py
```

4. Run an evaluation

1. Open [http://localhost:8501](http://localhost:8501) in your browser.
2. Inspect the available controls in the application.
3. Initiate an evaluation using the implemented workflow.
4. Review the generated responses and scores.
5. Inspect the output artifacts and logs for errors, missing data, or unexpected behavior.

The actual evaluation steps and available controls depend on the current application implementation.

## Evaluation Metrics

The evaluation framework is organized around five dimensions. Each dimension addresses a different aspect of response quality and helps distinguish one failure mode from another.

| Attribute | Evaluation Focus | Failure Modes to Detect |
|---|---|---|
| `correctness` | Technical and factual accuracy | Incorrect claims, invalid commands, and flawed architectural recommendations. |
| `completeness` | Coverage of required information | Missing prerequisites, omitted procedural steps, and overlooked operational warnings. |
| `relevance` | Alignment with the user's query | Irrelevant details, unnecessary elaboration, and responses that fail to address the question. |
| `groundedness` | Support from retrieved context | Unsupported claims, hallucinated details, and failure to acknowledge insufficient evidence. |
| `citation_accuracy` | Citation validity and support | Incorrect references, mismatched citations, and citations that do not substantiate the associated claims. |

### Evaluation Principles

**Correctness and groundedness are distinct.** A response can contain a factually correct statement that is not supported by the retrieved context. Conversely, a response can accurately reflect its context even when that context contains an error.

**Completeness is task-dependent.** A response should include the information required to answer the question, including relevant prerequisites and safety warnings, without assuming that every answer needs to be exhaustive.

**Citation accuracy requires evidence.** A citation should be checked for both validity and whether the cited source supports the associated claim. A correctly formatted URL is not necessarily a correct citation.

**Groundedness does not automatically imply refusal.** When retrieved context is insufficient, the expected behavior should be defined by the evaluation rubric. This may involve acknowledging uncertainty, requesting clarification, or declining to make unsupported claims.

### LLM-as-a-Judge Considerations

An LLM-as-a-judge evaluates a model response against specified criteria and produces an assessment. Its reliability depends on the judge prompt, rubric clarity, available evidence, model behavior, and output validation.

If the judge is configured with a temperature of `0`, this may reduce response variability, but it does not guarantee perfectly deterministic results.

The evaluation output format must also be verified. Structured numeric scores, binary labels, textual explanations, and aggregate scores are different representations and should not be treated as interchangeable.

## Evaluation Workflow

The intended end-to-end workflow consists of the following stages:

1. **Prepare the knowledge base:** Process technical documentation and index the resulting content.
2. **Retrieve context:** Search the vector database for content relevant to each test query.
3. **Generate a response:** Pass the query and relevant context to the configured language model.
4. **Evaluate the response:** Assess the generated answer against the five evaluation dimensions.
5. **Record the results:** Preserve scores, explanations, and relevant evaluation artifacts.
6. **Analyze failures:** Identify recurring problems and determine whether they originate in retrieval, generation, documentation, or evaluation logic.
7. **Improve and retest:** Modify the relevant component and rerun the same test cases to compare outcomes.

These stages describe the evaluation methodology. Their implementation and the completeness of the data flow should be verified against the project code.

## Validation and Limitations

A functioning demonstration is not, by itself, evidence of production readiness or scientific validity.

Before making stronger claims about the framework, validate the following:

- **Retrieval:** Confirm that relevant document chunks are retrieved for representative queries.
- **Generation:** Verify that model responses use the supplied context as intended.
- **Scoring:** Confirm that each evaluation dimension follows a documented rubric.
- **Output validation:** Check that judge responses conform to the expected schema and handle malformed output safely.
- **Repeatability:** Run identical test cases more than once and examine score variability.
- **Human agreement:** Compare judge assessments against human-reviewed examples.
- **Failure handling:** Test missing context, API errors, malformed responses, and empty retrieval results.
- **Result persistence:** Verify that evaluation results can be inspected and compared across runs.

Milvus Lite provides a local vector database option, but using it does not make the entire application production-ready. Production deployment would require additional consideration of security, access control, observability, error handling, data lifecycle management, and evaluation reliability.

## Project Goals

This project aims to demonstrate a systematic approach to RAG evaluation by combining technical documentation, retrieval, response generation, and multi-dimensional quality assessment.

Its core goals are to:

- Make RAG failure modes explicit and measurable.
- Evaluate correctness, completeness, relevance, groundedness, and citation accuracy independently.
- Support repeatable experiments using a consistent test dataset and rubric.
- Separate retrieval and generation problems from evaluation and scoring problems.
- Produce evidence that can guide improvements to documentation and RAG behavior.

The central principle is that **reliable RAG evaluation requires more than a plausible answer or a single aggregate score**. It requires clear evaluation criteria, traceable evidence, representative test cases, and a documented understanding of what each result establishes.

# SDG Research Agent

A multi-agent AI system for sustainable development research and evidence-based policy generation, powered by LangGraph, CrewAI, ChromaDB (RAG), and Streamlit.

## Project Structure

```text
d:\sdg-research-agent/
├── data/
│   ├── documents/        # PDF reports from UN/World Bank (RAG Source)
│   └── chromadb/         # Persistent vector database
├── agents/               # CrewAI Agent definitions and crew builder
├── tools/                # RAG, World Bank Indicators, and Semantic Scholar APIs
├── rag/                  # Document chunking, vector indexing, and retriever helpers
├── workflow/             # LangGraph state management and execution path (checkpointing & interrupts)
├── schemas/              # Pydantic v2 schemas for policy briefs and evaluation outputs
├── evaluation/           # LLM-as-Judge validation suite
├── ui/                   # Streamlit Frontend app dashboard
├── config.py             # Global project configuration management
├── main.py               # Main CLI entry point
├── requirements.txt      # Dependency specification
└── .env                  # Environment keys
```

---

## 📚 Ingested Documents (Knowledge Base)
By default, the RAG knowledge base indexes the following PDF reports located in `data/documents/`:
1.  **HDR_2023_24.pdf** – UNDP Human Development Report 2023-24
2.  **HDR_2025.pdf** – UNDP Human Development Report 2025
3.  **ITU_Digital_Development_2023.pdf** – ITU Facts and Figures 2023 on Digital Development
4.  **SDG_Progress_Report_2023.pdf** – UN Special Edition SDG Progress Report
5.  **WorldBank_Digital_Progress_2023.pdf** – World Bank Digital Progress Report 2023

### How to Expand the Knowledge Base
To ingest new sustainability documents or updated reports:
1.  Place your new PDF files directly into the `data/documents/` folder.
2.  Re-run the ingestion pipeline script:
    ```bash
    python rag/ingest.py
    ```
    *Note: The script checks for existing documents and will index and merge the new documents into the persistent ChromaDB collection.*

---

## 🤖 Multi-Agent Roles
The pipeline features five specialised agents configured in sequential sequence:
1.  **Research Specialist** (`research_agent.py`): Queries the local vector database (RAG) and external databases (World Bank API, Semantic Scholar) to compile fact-based evidence.
2.  **Quantitative Data Analyst** (`data_analyst_agent.py`): Performs quantitative assessment, checks statistical correlations, and isolates core indicators.
3.  **Policy Analyst** (`policy_analyst_agent.py`): Maps findings into development barriers and draft strategic policy recommendations.
4.  **SDG Alignment Specialist** (`sdg_alignment_agent.py`): Maps findings and policy solutions directly to UN SDGs, targets, and indicator codes.
5.  **Policy Brief Writer** (`report_writer_agent.py`): Synthesizes agent inputs into a formal, JSON-compliant Pydantic `PolicyBrief`.

---

## 🚀 Execution & Verification

### Prerequisites
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Set up environment keys in `.env` (ensure `GOOGLE_API_KEY` is active).

### CLI Mode (Verification)
Run the end-to-end command-line execution:
```bash
python main.py --query "digital divide in rural Pakistan"
```

### Streamlit Frontend Dashboard
To run the user-facing Streamlit application with human-in-the-loop checkpoint approval:
```bash
streamlit run ui/app.py
```
*   **Sidebar**: Select your model and adjust retrieval results.
*   **Stage 1**: Watch nodes execute in real time.
*   **Stage 2**: Inspect compiled data and click **Approve** or **Reject**.
*   **Stage 3 & 4**: View formatted brief, download plain text or JSON output, and inspect the LLM-as-Judge scores.

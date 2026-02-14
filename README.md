# Provenance Autonomous Research Agent

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Provenance** is a lightweight, autonomous research agent designed to execute multi-step research tasks with verifiable grounding. Unlike generic chatbots, Provenance iteratively searches, fetches, reads, and reasons about web content to produce evidence-backed answers.

## 🚀 Key Features

- **Autonomous Loop**: Cycles through *Search* → *Fetch* → *Reason* steps until the goal is satisfied.
- **Verifiable Evidence**: Every claim is linked to a specific chunk of text from a real URL.
- **Context-Aware Retrieval**: Uses semantic context blocks to ground reasoning, minimizing hallucinations.
- **Robust Searching**: Integration with DuckDuckGo for broad web coverage.
- **Resilient Execution**: includes retry logic, robot.txt compliance, and anti-stagnation heuristics.

## 🛠️ Architecture

The agent operates on a **Constraint-Based Execution Model**:

1.  **Orchestrator**: Manages the state, step constraints, and action planning.
2.  **Tools Layer**:
    *   **HTTP**: Safe fetching with timeout management and user-agent rotation.
    *   **Crawl**: Respects `robots.txt` and validates HTML structure.
    *   **Search**: Query formulation and result parsing.
3.  **LLM Core**: Uses Groq (e.g., Mixtral/Qwen) for fast, deterministic reasoning and planning.

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/DEBA-GLITCH/Provenance_web_crawler.git
    cd Provenance_web_crawler
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Copy the example environment file and add your API keys.
    ```bash
    cp .env.example .env
    ```
    
    Edit `.env`:
    ```ini
    GROQ_API_KEY=gsk_...
    GROQ_MODEL=mixtral-8x7b-32768
    ```

## 🚦 Usage

Run the agent by providing a specific research goal.

```bash
python main.py --goal "What are the latest breakthroughs in solid-state battery technology form 2024-2025?"
```

### Output

The agent will print its thought process in real-time:
- `🔎 SEARCH`: Queries executed.
- `🌐 FETCH`: URLs visited.
- `🧠 REASON`: Analysis of gathered evidence.
- `🎯 SUCCESS`: Final answer with confidence score.

Evidence data is stored locally in `evidence_data/` for auditing.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

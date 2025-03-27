# Lightweight LLM Search Agent

## Overview
This project implements a highly efficient, lightweight search agent powered by small, quantized LLMs to replicate a "Perplexity-like" web search experience. The core strength of this pipeline is its capability to perform accurate internet searches and content retrieval using low-parameter, quantized Large Language Models (LLMs) like Gemma3 (4b-it-fp16).

## Approach and Unique Selling Point (USP)
Traditional search-integrated LLM applications often depend on large, resource-intensive models (20B parameters or higher). However, this project leverages smaller, quantized models (1B, 3B, 4B, 7B, 8B parameters) capable of running efficiently even on modest hardware setups.

### Key Advantages:
- **Efficiency**: Lightweight models significantly reduce computational and memory requirements.
- **Accessibility**: Models are easy to deploy locally, even without GPU acceleration.
- **Scalability**: Ideal for integration into edge devices, personal laptops, and resource-constrained servers.
- **Cost-effectiveness**: Reduced reliance on expensive cloud resources and high-end GPUs.

### Pipeline Breakdown:
- **Search Classification**: Determines whether a user query requires a web search.
- **Query Generation**: Generates optimized web search queries using the Gemma3 LLM.
- **Web Scraping**: Uses DuckDuckGo for fast, privacy-oriented web scraping.
- **Content Extraction & Validation**: Implements Trafilatura to extract meaningful text from web pages and validate relevancy using the same lightweight LLM.

## Getting Started

### Prerequisites:
- Python 3.8 or higher
- Ollama (an easy-to-use platform for running and managing LLMs locally)

#### Ollama Installation
Visit [Ollama's official page](https://ollama.ai/) for downloads and installation guidance:
- **Download Ollama**: [https://ollama.ai/download](https://ollama.ai/download)
- **Gemma3 (4b-it-fp16) Model**:

```bash
ollama pull gemma:4b-it-fp16
```

### Clone and Setup Project:

```bash
git clone https://github.com/Vasu-yadav/MySearchAgent.git
cd MySearchAgent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Project:

```bash
python agent.py
```

## Why This Approach Works

The critical innovation here is using small, quantized models combined with a structured, AI-assisted web-search pipeline. By strategically placing lightweight models at crucial decision points (search need identification, query optimization, result ranking, and relevancy validation), the system achieves high accuracy comparable to much larger models. This targeted usage of smaller LLMs ensures computational efficiency without compromising quality.

## Future Prospects
- **Model Diversification**: Experiment with various quantized models to further optimize performance and accuracy.
- **Edge Deployment**: Adaptation of this pipeline for embedded devices and mobile platforms.
- **Enhanced Result Validation**: Integration of reinforcement learning techniques for improved query optimization and result relevance.
- **UI/UX Improvements**: Develop intuitive user interfaces enhancing the overall user experience and interaction.

---

By implementing this lightweight LLM-based web search pipeline, this project paves the way for accessible, efficient, and accurate AI-powered search experiences suitable for a broad spectrum of devices and environments.


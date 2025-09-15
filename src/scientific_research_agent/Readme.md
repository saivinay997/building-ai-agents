# Scientific AI Research Assistant Agent (SAIRAA)

This project implements an intelligent research assistant that helps users navigate, understand, and analyze scientific literature using LangGraph and advanced language models. By combining various academic API with sophisticated paper processing techniques, it creates a seamless experience for researchers, students, and professionals working with academic papers.

> NOTE: The presented workflow is not domain specific: each step in the graph can be adapted to a different domain by simply changing the prompts.

## Motivation

Research literature review represents a significant time investment in R&D, with studies showing that researchers spend 30-50% of their time reading, analyzing, and synthesizing academic papers. This challenge is universal across the research community. While thorough literature review is crucial for advancing science and technology, the current process remains inefficient and time-consuming.

Key challenges include:
- Extensive time commitment (30-50% of R&D hours) dedicated to reading and processing papers
- Inefficient search processes across fragmented database ecosystems
- Complex task of synthesizing and connecting findings across multiple papers
- Resource-intensive maintenance of comprehensive literature reviews
- Ongoing effort required to stay current with new publications

## Key components

 1. State-Driven Workflow Engine 
    - StateGraph Architecture: Five-node system for orchestrated research 
    - Decision Making Node: Query intent analysis and routing 
    - Planning Node: Research strategy formulation
    - Tool Execution Node: Paper retrieval and processing 
    - Judge Node: Quality validation and improvement cycles 

2. Paper Processing Integration 
    - Source Integration, CORE API for comprehensive paper access 
    - Document Processing, PDF content extraction, Text structure preservation 

3. Analysis Workflow 
    - State-aware processing pipeline 
    - Multi-step validation gates 
    - Quality-focused improvement cycles 
    - Human-in-the-loop validation options

## Method details

1. The system requires 
    - OpenAI API key to access GPT 4o. This model was chosen after comparing its performance with other, open-source alternatives (in particular Llama 3). However, any other LLM with tool calling capabilities can be used.
    - CORE API key for paper retrieval. CORE is one of the larges online repositories for scientific papers, counting over 136 million papers, and offers a free API for personal use. A key can be requested [here](https://core.ac.uk/services/api#form).

2. Technical Architecture: 
    - LangGraph for state orchestration.
    - PDFplumber for document processing.
    - Pydantic for structured data handling.
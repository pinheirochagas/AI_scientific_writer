# AI Scientific Writer

A comprehensive agentic workflow for transforming scientific transcripts into publication-ready perspective articles.

## Overview

AI Scientific Writer is a specialized AI system that transforms spoken content and presentation materials into high-quality scientific articles with proper citations. The system implements a multi-agent workflow that handles the entire process from transcript conversion to citation management.

## Technical Implementation

- Built with Python 3.11 and Microsoft Azure OpenAI via UCSF Versa
- Uses specialized models based on task requirements:
  - Whisper-3-large for audio transcription
  - GPT-4o-2024-08-06 for slide captioning and citation scaffolding
  - o1-2024-12-17 for draft generation and improvements
- Processes run on an 8-vCPU virtual machine, requiring approximately 14 minutes per complete run
- Implements structured data validation and comprehensive error handling

## Workflow Architecture

The system consists of seven specialized agents that work together in a pipeline:

### 1. PubMed Agent
- **Input**: Search query related to the paper topic
- **Process**: Queries PubMed API and retrieves comprehensive scientific paper data
- **Output**: JSON file with paper details (titles, authors, abstracts, journals)

### 2. Transcript-to-Perspective Agent
- **Input**: Transcript of a talk/interview
- **Process**: Converts spoken content into formal scientific perspective
- **Output**: Structured scientific article maintaining personal perspective

### 3. Article Review Agent
- **Input**: Draft article and original transcript
- **Process**: Performs comprehensive analysis including:
  - Scholarly rigor assessment
  - Narrative coherence evaluation
  - Transition and flow analysis using NLP techniques
  - Publication readiness rating
- **Output**: Structured review feedback with quantitative metrics

### 4. Article Improvement Agent
- **Input**: Article draft, review feedback, and original transcript
- **Process**: Refines article based on reviewer feedback
- **Output**: Improved article version

### 5. Reference Marking Agent
- **Input**: Improved article
- **Process**: Identifies statements requiring citations and inserts [REF] markers
- **Output**: Article with reference markers


### 6. Reference Matching Agent
- **Input**: Manuscript text and PubMed search results
- **Process**: Extracts key statements and ranks available references by relevance
- **Output**: Structured JSON with statements and ranked reference suggestions

## Data Flow

The workflow follows this sequence:

1. Audio and slides are processed into a unified transcript
2. PubMed agent retrieves relevant scientific literature
3. Draft generation creates an initial manuscript
4. Citation scaffolding inserts reference placeholders
5. Multiple review-improvement cycles enhance quality
6. Reference resolution matches citations to appropriate sources

Each output is saved to maintain version history.

## Key Features

- **Multimodal Input Processing**: Handles both audio and visual content
- **Iterative Improvement**: Multiple review-improvement cycles enhance quality
- **Citation Management**: Automated citation marking and matching
- **Semantic Matching**: Uses semantic similarity for reference resolution
- **Computational Efficiency**: Complete pipeline runs in approximately 14 minutes

## Outputs

The system produces:
- Formatted, citation-rich manuscript
- Ranked references JSON file
- Comprehensive intermediate outputs for reproducibility

## Usage

The system can be used through two main workflows:

1. **Complete Pipeline** (main.py): Full workflow from transcript to cited article
2. **Reference Management** (pipeline.py): Extract key statements and match references

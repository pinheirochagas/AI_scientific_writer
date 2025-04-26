# Scientific Writer Versa

A comprehensive agentic workflow for transforming scientific transcripts into publication-ready perspective articles.

## Overview

Scientific Writer Versa is a specialized AI system that transforms spoken content into high-quality scientific articles with proper citations. The system implements a multi-agent workflow that handles the entire process from transcript conversion to citation management.

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
- **Input**: Marked article and PubMed search results
- **Process**: Matches each reference marker with appropriate citations
- **Output**: Complete article with formatted citations

### 7. Reference Ranking Agent
- **Input**: Manuscript text and PubMed search results
- **Process**: Extracts key statements and ranks available references by relevance
- **Output**: Structured JSON with statements and ranked reference suggestions

## Data Flow

The workflow follows this sequence:

1. PubMed agent retrieves relevant scientific literature
2. Transcript is converted to a perspective article
3. The article undergoes multiple review-improvement cycles:
   - Review agent analyzes the article
   - Improvement agent enhances based on feedback
4. Reference markers are inserted at appropriate points
5. References are matched to markers using PubMed results

Each output is saved with timestamps to maintain version history.

## Key Features

- **Iterative Improvement**: Multiple review-improvement cycles enhance quality
- **Narrative Analysis**: Sophisticated text analytics for flow and transitions
- **Citation Management**: Automated citation marking and matching
- **Structured Output**: Each stage produces well-formatted outputs
- **Versioning**: Timestamped files for tracking changes

## Technical Implementation

- Built with Azure OpenAI API
- Uses different models based on task complexity
- Implements Pydantic schemas for structured data validation
- NLP techniques for text analysis (NLTK)
- Comprehensive error handling and logging

## Usage

The system can be used through two main workflows:

1. **Complete Pipeline** (main.py): Full workflow from transcript to cited article
2. **Reference Management** (pipeline.py): Extract key statements and match references

## Requirements

- Python 3.8+
- Azure OpenAI API access
- NLTK and other dependencies
- Internet connection for PubMed API access
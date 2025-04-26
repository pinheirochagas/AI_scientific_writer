import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Import agent functions
from agents.pubmed_agent import run_pubmed_agent
from agents.transcript_to_perspective_agent import run_transcript_agent
from agents.reference_marking_agent import run_reference_marking_agent
from agents.reference_matching_agent import run_reference_matching_agent
from agents.article_review_agent import run_article_review_agent
from agents.article_improvement_agent import run_article_improvement_agent


def main():
    """Run the agentic AI scientific writer pipeline."""
    
    # # Check for OpenAI API key
    if not os.getenv("VERSA_OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please create a .env file with your OpenAI API key.")
        sys.exit(1)
    
    # # Get current timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # # Hard-coded input parameters
    transcript_path = "data/transcript/marilu_transcript.txt"
    topic = "Marilu Gorno-Tempini about primary progressive aphasia"
    pubmed_query = "Boon Lead Tee AND PPA"
    
    # Define output paths with timestamps
    pubmed_output = f"data/pubmed/search_results_{timestamp}.json"
    perspective_output = f"data/perspective/perspective_article_{timestamp}.txt"
    marked_output = f"data/marked/marked_article_{timestamp}.txt"
    references_output = f"data/references/article_with_references_{timestamp}.txt"
    
    # Step 1: Search PubMed
    print("\n--- Step 1: Searching PubMed ---")
    pubmed_output = run_pubmed_agent(pubmed_query, pubmed_output)
    
    # Step 2: Convert transcript to perspective article
    print("\n--- Step 2: Converting transcript to perspective article ---")
    perspective_output = run_transcript_agent(transcript_path, topic, perspective_output)
    
    # Steps 3-5: Iterative review and improvement (3 cycles)
    current_article = perspective_output

    # Read the article file
    current_article = "data/references/article_with_references_20250322_184343.txt"
    
    for i in range(3):
        print(f"\n--- Iteration {i+1}: Review and Improvement ---")
        
        # Step 3: Review article
        review_output = f"data/review/review_feedback_{i+1}_{timestamp}.txt"
        review_output = run_article_review_agent(current_article, transcript_path, review_output)
        
        # Step 4: Improve article
        improved_output = f"data/improved/improved_article_{i+1}_{timestamp}.txt"
        improved_output = run_article_improvement_agent(current_article, review_output, transcript_path, improved_output)
        
        # Update current article for next iteration
        current_article = improved_output
    
    # Step 5: Insert reference markers (moved after iterations)
    print("\n--- Step 5: Inserting reference markers ---")
    marked_output = run_reference_marking_agent(current_article, marked_output)
    
    # Step 6: Match references (moved after iterations)
    print("\n--- Step 6: Matching references to markers ---")
    references_output = run_reference_matching_agent(marked_output, pubmed_output, references_output)
    
    print("\n--- Process completed successfully ---")
    print(f"Final article with references saved to: {references_output}")

if __name__ == "__main__":
    main()
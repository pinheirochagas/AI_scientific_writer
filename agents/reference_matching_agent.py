import os
import json
from openai import AzureOpenAI
from typing import Dict, Any, List

def match_references(marked_article: str, references_json: List[Dict[str, Any]], output_path: str) -> str:
    """
    Match reference markers in the article with references from the JSON file.
    
    Args:
        marked_article: The article text with [REF] markers.
        references_json: List of references from PubMed.
        output_path: Path to save the article with matched references.
        
    Returns:
        Path to the saved article file with matched references.
    """
    client = AzureOpenAI(
        api_key=os.environ["VERSA_OPENAI_API_KEY"],
        api_version=os.environ['VERSA_API_VERSION'],
        azure_endpoint=os.environ['VERSA_RESOURCE_ENDPOINT']
    )
    
    # Convert references to string for prompt
    references_str = json.dumps(references_json, indent=2)
    
    prompt = f"""
    You will receive a JSON file containing a list of references. Your task is to accurately match and allocate the references from this JSON file to each "[REF]" marker previously inserted into the manuscript. Ensure that each inserted "[REF]" is associated with the most appropriate reference from the provided list, carefully considering the context and relevance of each reference to the statement it supports. Only use references provided in the JSON file. If no matching reference is found for a particular "[REF]" marker, leave it as "[REF not found]". The citations should be formatted in APA Style with in-text citations and reference list.

    Here is the manuscript with [REF] markers:
    
    {marked_article}
    
    Here are the available references (JSON format):
    
    {references_str}
    """
    
    print("Matching references to citation markers")
    
    response = client.chat.completions.create(
        model="o1-2024-12-17",
        messages=[
            {"role": "user", "content": prompt}
        ],
        reasoning_effort="high"
    )
    
    article_with_references = response.choices[0].message.content

    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the article with references to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(article_with_references)
    
    print(f"References matched and saved to {output_path}")
    return output_path

def run_reference_matching_agent(marked_article_path: str, references_json_path: str, output_path: str) -> str:
    """
    Run the reference matching agent.
    
    Args:
        marked_article_path: Path to the article with [REF] markers.
        references_json_path: Path to the JSON file with references.
        output_path: Path to save the article with matched references.
        
    Returns:
        Path to the saved article file with matched references.
    """
    # Read the marked article
    with open(marked_article_path, 'r', encoding='utf-8') as f:
        marked_article = f.read()
    
    # Read the references JSON
    with open(references_json_path, 'r', encoding='utf-8') as f:
        references_json = json.load(f)
    
    return match_references(marked_article, references_json, output_path)

if __name__ == "__main__":
    # Test the agent
    test_marked_article_path = "test_marked_perspective.txt"
    test_references_json_path = "test_pubmed_results.json"
    test_output_path = "test_perspective_with_references.txt"
    
    # Create test files if they don't exist
    if not os.path.exists(test_marked_article_path):
        with open(test_marked_article_path, 'w', encoding='utf-8') as f:
            f.write("Recent studies suggest a significant correlation between sleep and memory consolidation.[REF]")
    
    if not os.path.exists(test_references_json_path):
        test_references = [
            {
                "pmid": "12345678",
                "title": "Sleep and memory consolidation: A review",
                "authors": ["Smith, J", "Doe, A"],
                "year": "2020",
                "journal": "Journal of Sleep Research",
                "abstract": "This paper reviews the relationship between sleep and memory consolidation."
            }
        ]
        with open(test_references_json_path, 'w', encoding='utf-8') as f:
            json.dump(test_references, f, indent=2)
    
    run_reference_matching_agent(test_marked_article_path, test_references_json_path, test_output_path)
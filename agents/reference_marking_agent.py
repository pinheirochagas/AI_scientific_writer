import os
from openai import AzureOpenAI
from typing import Dict, Any

def insert_reference_markers(article_text: str, output_path: str) -> str:
    """
    Insert [REF] markers where citations are needed in the article.
    
    Args:
        article_text: The perspective article text.
        output_path: Path to save the marked article.
        
    Returns:
        Path to the saved marked article file.
    """
    client = AzureOpenAI(
        api_key=os.environ["VERSA_OPENAI_API_KEY"],
        api_version=os.environ['VERSA_API_VERSION'],
        azure_endpoint=os.environ['VERSA_RESOURCE_ENDPOINT']
    )
    
    prompt = f"""
    You will be provided with a scientific manuscript. Your task is to carefully read the provided text and insert "[REF]" immediately following claims or statements that clearly requires a citation. Do not make any modifications to the wording, punctuation, or formatting of the original text. 

    Example:
    Original:
    "Recent studies suggest a significant correlation between sleep and memory consolidation."

    Modified:
    "Recent studies suggest a significant correlation between sleep and memory consolidation [REF]."

    Here is the scientific manuscript:
    
    {article_text}
    """
    
    print("Inserting reference markers into perspective article")
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06", #"o1-mini-2024-09-12",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format=ArticleReview
    )
    
    marked_article = response.choices[0].message.content
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the marked article to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(marked_article)
    
    print(f"Reference markers inserted and saved to {output_path}")
    return output_path

def run_reference_marking_agent(article_path: str, output_path: str) -> str:
    """
    Run the reference marking agent.
    
    Args:
        article_path: Path to the perspective article file.
        output_path: Path to save the marked article.
        
    Returns:
        Path to the saved marked article file.
    """
    # Read the article
    with open(article_path, 'r', encoding='utf-8') as f:
        article_text = f.read()
    
    return insert_reference_markers(article_text, output_path)

if __name__ == "__main__":
    # Test the agent
    test_article_path = "test_perspective.txt"
    test_output_path = "test_marked_perspective.txt"
    
    # Create a test article file if it doesn't exist
    if not os.path.exists(test_article_path):
        with open(test_article_path, 'w', encoding='utf-8') as f:
            f.write("Recent studies suggest a significant correlation between sleep and memory consolidation.")
    
    run_reference_marking_agent(test_article_path, test_output_path)
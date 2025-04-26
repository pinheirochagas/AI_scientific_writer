import os
from openai import AzureOpenAI
from typing import Dict, Any

def improve_article(article_text: str, review_feedback: str, transcript_text: str, output_path: str) -> str:
    """
    Improve the article based on review feedback.
    
    Args:
        article_text: The article text with references.
        review_feedback: The review feedback for improvement.
        transcript_text: The original transcript text.
        output_path: Path to save the improved article.
        
    Returns:
        Path to the saved improved article file.
    """
    client = AzureOpenAI(
        api_key=os.environ["VERSA_OPENAI_API_KEY"],
        api_version=os.environ['VERSA_API_VERSION'],
        azure_endpoint=os.environ['VERSA_RESOURCE_ENDPOINT']
    )
    
    prompt = f"""
    You are an experienced scientific writer tasked with refining and improving a scientific perspective article based on constructive feedback provided by an expert reviewer. Your goal is to thoughtfully incorporate the reviewer's suggestions, enhancing the manuscript's clarity, coherence, scholarly rigor, and intellectual contribution.
    
    Here is the current version of the article:
    
    {article_text}
    
    Here is the review feedback:
    
    {review_feedback}
    
    Here is the original transcript that was used to create this article:
    
    {transcript_text}
    
    Please provide an improved version of the article based on the feedback. Maintain the same overall structure, but address all the issues raised by the reviewer.
    """
    
    print("Improving the article based on reviewer feedback")
    
    response = client.chat.completions.create(
        model="o1-2024-12-17",
        messages=[
            {"role": "user", "content": prompt}
        ],
        reasoning_effort="high"
    )
    
    improved_article = response.choices[0].message.content
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the improved article to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(improved_article)
    
    print(f"Improved article generated and saved to {output_path}")
    return output_path

def run_article_improvement_agent(article_path: str, review_feedback_path: str, transcript_path: str, output_path: str) -> str:
    """
    Run the article improvement agent.
    
    Args:
        article_path: Path to the article file with references.
        review_feedback_path: Path to the review feedback file.
        transcript_path: Path to the original transcript file.
        output_path: Path to save the improved article.
        
    Returns:
        Path to the saved improved article file.
    """
    # Read the article
    with open(article_path, 'r', encoding='utf-8') as f:
        article_text = f.read()
    
    # Read the review feedback
    with open(review_feedback_path, 'r', encoding='utf-8') as f:
        review_feedback = f.read()
    
    # Read the transcript
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_text = f.read()
    
    return improve_article(article_text, review_feedback, transcript_text, output_path)

if __name__ == "__main__":
    # Test the agent
    test_article_path = "test_perspective_with_references.txt"
    test_review_feedback_path = "test_review_feedback.txt"
    test_transcript_path = "test_transcript.txt"
    test_output_path = "test_improved_article.txt"
    
    # Create test files if they don't exist
    if not os.path.exists(test_article_path):
        with open(test_article_path, 'w', encoding='utf-8') as f:
            f.write("This is a test perspective article with references.")
    
    if not os.path.exists(test_review_feedback_path):
        with open(test_review_feedback_path, 'w', encoding='utf-8') as f:
            f.write("This article needs improvement in clarity and structure.")
    
    if not os.path.exists(test_transcript_path):
        with open(test_transcript_path, 'w', encoding='utf-8') as f:
            f.write("This is a test transcript for the article.")
    
    run_article_improvement_agent(test_article_path, test_review_feedback_path, test_transcript_path, test_output_path)
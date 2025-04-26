import os
from typing import Dict, Any
from openai import AzureOpenAI

def convert_transcript_to_perspective(transcript: str, topic: str, output_path: str) -> str:
    """
    Convert a transcript into a scientific perspective article.
    
    Args:
        transcript: The transcript text to convert.
        topic: The topic of the perspective article.
        output_path: Path to save the generated article.
        
    Returns:
        Path to the saved article file.
    """
    client = AzureOpenAI(
        api_key=os.environ["VERSA_OPENAI_API_KEY"],
        api_version=os.environ['VERSA_API_VERSION'],
        azure_endpoint=os.environ['VERSA_RESOURCE_ENDPOINT']
    )
    
    prompt = f"""

    Please convert the provided transcript into a scientific perspective article about the topic: {topic} following the guidelines above below:

    IMPORTANT INSTRUCTIONS:
    CRITICAL: Include ALL scientific content from the transcript. 
    1. Maintain the personal perspective, while adhering to the scientific content.
    2. DO NOT add any new scientific content, facts, or research that is not present in the transcript
    3. Only restructure and format the existing content to fit a perspective paper format
    4. You may clarify concepts mentioned in the transcript, but do not introduce topics not discussed
    5. No bullet points. 
    
    Below are some general guidelines for perspective articles:
    Perspective Article Guidelines: Perspective articles serve as a platform for authors to discuss models and ideas from a personal viewpoint. They are characterized by the following features:
    More forward-looking and speculative than Review articles
    May take a narrower field of view
    Can present opinionated viewpoints while maintaining balance
    Intended to stimulate discussion and new experimental approaches
    
    Format Requirements
    Begin with a 200-word maximum preface that sets the stage and ends with a summary sentence. 
    Minimum 8 pages, maximum 10 pages in length
    Target word count: minimum 4,000 and maximum 5,000 words
    
    Content Guidelines
    Focus on one topical aspect of a field rather than providing comprehensive literature surveys
    Can present controversial viewpoints but should briefly indicate opposing perspectives
    Should not focus primarily on the author's own work
    Use accessible language
    Define novel concepts
    Explain specialist terminology
        
    
    {transcript}
    """
    
    print(f"Converting transcript to perspective article about: {topic}")
    
    response = client.chat.completions.create(
        model="o1-2024-12-17",
        messages=[
            {"role": "user", "content": prompt}
        ],
        reasoning_effort="high"
    )
    
    perspective_article = response.choices[0].message.content
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the perspective article to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(perspective_article)
    
    print(f"Perspective article generated and saved to {output_path}")
    return output_path

def run_transcript_agent(transcript_path: str, topic: str, output_path: str) -> str:
    """
    Run the transcript to perspective article agent.
    
    Args:
        transcript_path: Path to the transcript file.
        topic: The topic of the perspective article.
        output_path: Path to save the generated article.
        
    Returns:
        Path to the saved article file.
    """
    # Read the transcript
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    return convert_transcript_to_perspective(transcript, topic, output_path)

if __name__ == "__main__":
    # Test the agent
    test_transcript_path = "test_transcript.txt"
    test_topic = "Marilu Gorno-Tempini about primary progressive aphasia"
    test_output_path = "test_perspective.txt"
    
    # Create a test transcript file if it doesn't exist
    if not os.path.exists(test_transcript_path):
        with open(test_transcript_path, 'w', encoding='utf-8') as f:
            f.write("This is a test transcript about primary progressive aphasia...")
    
    run_transcript_agent(test_transcript_path, test_topic, test_output_path)
import os
import re
import json
from openai import AzureOpenAI
from typing import Dict, Any, List, TypedDict, Optional
import nltk
from pydantic import BaseModel, Field

# Download NLTK resources if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from nltk.tokenize import sent_tokenize, word_tokenize

class NarrativeAnalyzer:
    """Analyzes narrative flow and transitions between paragraphs"""
    
    def __init__(self):
        self.transition_words = set([
            'moreover', 'furthermore', 'consequently', 'therefore',
            'however', 'nevertheless', 'indeed', 'specifically',
            'conversely', 'similarly', 'likewise', 'instead',
            'nonetheless', 'meanwhile', 'subsequently', 'ultimately'
        ])
    
    def analyze_transitions(self, text: str) -> Dict:
        """Analyze paragraph transitions and flow"""
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Analyze transition words usage
        transition_count = sum(1 for word in words if word.lower() in self.transition_words)
        
        # Analyze sentence and paragraph lengths
        sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
        paragraph_lengths = [len(word_tokenize(para)) for para in paragraphs]
        
        # Analyze first and last sentences of paragraphs for transitions
        paragraph_transitions = []
        for i in range(1, len(paragraphs)):
            prev_para_last = sent_tokenize(paragraphs[i-1])[-1] if sent_tokenize(paragraphs[i-1]) else ""
            curr_para_first = sent_tokenize(paragraphs[i])[0] if sent_tokenize(paragraphs[i]) else ""
            
            transition_quality = 0
            # Check for transition words at start of paragraph
            first_words = word_tokenize(curr_para_first.lower())[:3]
            if any(word in self.transition_words for word in first_words):
                transition_quality += 0.5
                
            # Check for thematic connection between paragraphs
            # (simplified: check for shared significant words)
            prev_words = set(word.lower() for word in word_tokenize(prev_para_last) 
                           if len(word) > 4 and word.isalpha())
            curr_words = set(word.lower() for word in word_tokenize(curr_para_first) 
                           if len(word) > 4 and word.isalpha())
            
            if prev_words.intersection(curr_words):
                transition_quality += 0.5
                
            paragraph_transitions.append(transition_quality)
        
        return {
            "transition_density": transition_count / max(len(paragraphs), 1),
            "avg_sentence_length": sum(sentence_lengths) / max(len(sentence_lengths), 1),
            "sentence_length_variance": self._variance(sentence_lengths),
            "avg_paragraph_length": sum(paragraph_lengths) / max(len(paragraph_lengths), 1),
            "paragraph_length_variance": self._variance(paragraph_lengths),
            "paragraph_transition_scores": paragraph_transitions,
            "avg_transition_quality": sum(paragraph_transitions) / max(len(paragraph_transitions), 1) if paragraph_transitions else 0
        }
    
    def _variance(self, numbers: List[int]) -> float:
        if not numbers:
            return 0
        mean = sum(numbers) / len(numbers)
        return sum((x - mean) ** 2 for x in numbers) / len(numbers)

# Define Pydantic models for structured output
class OverallAssessment(BaseModel):
    scholarly_rigor: float = Field(..., description="Rating of scholarly rigor from 0-1")
    narrative_coherence: float = Field(..., description="Rating of narrative coherence from 0-1")
    publication_readiness: float = Field(..., description="Rating of publication readiness from 0-1")

class NarrativeFlowAssessment(BaseModel):
    paragraph_transitions: float = Field(..., description="Rating of paragraph transitions from 0-1")
    logical_progression: float = Field(..., description="Rating of logical progression from 0-1")
    thematic_consistency: float = Field(..., description="Rating of thematic consistency from 0-1")
    section_balance: float = Field(..., description="Rating of section balance from 0-1")

class TransitionFeedback(BaseModel):
    location: str = Field(..., description="Description of where the transition issue occurs")
    issue: str = Field(..., description="Description of the transition problem")
    suggestion: str = Field(..., description="Specific recommendation for improvement")

class ContentRecommendations(BaseModel):
    conceptual_framework: str = Field(..., description="Recommendation for improving conceptual framework")
    terminology: str = Field(..., description="Recommendation for improving terminology usage")
    balancing_perspectives: str = Field(..., description="Recommendation for better balancing of perspectives")
    supporting_evidence: str = Field(..., description="Recommendation for improving supporting evidence")

class ArticleReview(BaseModel):
    overall_assessment: OverallAssessment
    narrative_flow_assessment: NarrativeFlowAssessment
    major_strengths: List[str] = Field(..., description="List of major strengths of the article")
    areas_for_improvement: List[str] = Field(..., description="List of areas for improvement")
    specific_transition_feedback: List[TransitionFeedback] = Field(..., description="Specific feedback on paragraph transitions")
    content_recommendations: ContentRecommendations
    summary_evaluation: str = Field(..., description="Overall conclusion of the evaluation (250-300 words)")

def review_article(article_text: str, transcript_text: str, output_path: str) -> str:
    """
    Review the article and provide feedback for improvement.
    
    Args:
        article_text: The article text with references.
        transcript_text: The original transcript text.
        output_path: Path to save the review feedback.
        
    Returns:
        Path to the saved review feedback file.
    """
    # Create narrative analyzer
    narrative_analyzer = NarrativeAnalyzer()
    narrative_analysis = narrative_analyzer.analyze_transitions(article_text)
    
    client = AzureOpenAI(
        api_key=os.environ["VERSA_OPENAI_API_KEY"],
        api_version=os.environ['VERSA_API_VERSION'],
        azure_endpoint=os.environ['VERSA_RESOURCE_ENDPOINT']
    )
    
    # Extract word count
    word_count = len(word_tokenize(article_text))
    
    prompt = f"""
    # LLM Instructions for Reviewing Scientific Perspective Articles
    You are an expert scientific reviewer tasked with evaluating and providing feedback on a scientific perspective article. Your analysis should embody the highest standards of academic rigor while offering constructive guidance to improve the manuscript.
    
    ## Evaluation Framework
    Assess the perspective article through these interconnected dimensions, providing thoughtful analysis that emerges naturally from your expert understanding:
    Examine how effectively the article presents forward-looking ideas and speculative models within a focused field, rather than attempting a comprehensive literature survey. Consider whether the author maintains balance while expressing personal viewpoints, and how well the article stimulates discussion and new experimental approaches.
    Assess the article's conceptual foundations and theoretical coherence. Determine whether ideas develop logically and if the author effectively establishes connections between existing knowledge and proposed conceptual innovations.
    Evaluate the accessibility of language, clarity of novel concept definitions, and explanations of specialist terminology. Consider how well the author communicates complex ideas to readers who may not be specialists in the specific subfield.
    Analyze how the author engages with opposing viewpoints while maintaining their perspective. Consider whether the article acknowledges limitations and uncertainties appropriately.
    
    ## Content Analysis
    Your review should address:
    - How effectively the preface (maximum 200 words) sets the stage and summarizes the key message
    - Whether the perspective maintains appropriate scope and focus on a specific topical aspect
    - Balance between presenting personal viewpoints and acknowledging alternative perspectives
    - Use of accessible language and clear definitions of novel concepts
    - Integration and explanation of specialist terminology
    - Appropriate length (Minimum 8 pages, maximum 10 pages with minimum 4,000 and maximum 5,000 words)
    
    ## Scholarly Standards
    Your analysis should provide sophisticated engagement with:
    - Theoretical coherence and intellectual rigor of the perspective
    - Integration of the perspective within the broader scientific discourse
    - Potential impact on stimulating discussion and new experimental approaches
    - Balance between speculation and evidence-based reasoning
    - Originality and innovative thinking within established scientific frameworks
    
    ## Narrative Flow Analysis
    Pay special attention to the flow and transitions between paragraphs. The article shows the following metrics:
    - Current word count: {word_count} words
    - Average paragraph length: {narrative_analysis['avg_paragraph_length']:.2f} words
    - Paragraph length variance: {narrative_analysis['paragraph_length_variance']:.2f}
    - Average transition quality between paragraphs: {narrative_analysis['avg_transition_quality']:.2f} (scale 0-1)
    - Transition word density: {narrative_analysis['transition_density']:.2f} per paragraph
    
    Provide specific feedback on how to improve narrative flow and paragraph transitions. Look for abrupt topic changes, disconnected ideas, and opportunities to create more coherent progression of thought.
    
    ## Feedback Approach
    Develop your analysis through a thoughtful progression:
    Begin by situating your evaluation within the context of the article's aims and field. Allow your assessment to emerge organically from engagement with the manuscript's strengths and limitations.
    Develop your critique through careful consideration of the perspective's contributions, building complexity while maintaining clarity about essential improvements needed.
    Integrate suggestions for enhancement naturally within your analytical flow, connecting them to specific elements of the manuscript.
    Maintain a tone that is rigorous yet constructive, scholarly yet accessible, and critical yet respectful of the author's intellectual contributions.
    
    Here is the article to review:
    
    {article_text}
    
    Here is the original transcript that was used to create this article:
    
    {transcript_text}
    """
    
    print("Reviewing the perspective article")
    
    # Use beta.chat.completions with direct Pydantic model specification
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06", #"o1-mini-2024-09-12",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format=ArticleReview
    )
    
    # Parse the string response into a structured format
    review_output = response.choices[0].message.content
    
    # Method 1: If the output is already JSON-formatted
    try:
        raw_result = json.loads(review_output)
        article_review = ArticleReview(**raw_result)
        review_feedback = article_review.model_dump()
    except (json.JSONDecodeError, TypeError, ValueError):
        # Method 2: If there's an issue with JSON parsing or model validation
        # Just use the raw string output in this fallback case
        review_feedback = review_output
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the review feedback to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(review_feedback, f, indent=2)
    
    # Also save narrative analysis separately
    narrative_output_path = os.path.join(os.path.dirname(output_path), 
                                        os.path.basename(output_path).split('.')[0] + '_narrative_analysis.json')
    with open(narrative_output_path, 'w', encoding='utf-8') as f:
        json.dump(narrative_analysis, f, indent=2)
    
    print(f"Review feedback generated and saved to {output_path}")
    print(f"Narrative analysis saved to {narrative_output_path}")
    
    return output_path

def run_article_review_agent(article_path: str, transcript_path: str, output_path: str) -> str:
    """
    Run the article review agent.
    
    Args:
        article_path: Path to the article file with references.
        transcript_path: Path to the original transcript file.
        output_path: Path to save the review feedback.
        
    Returns:
        Path to the saved review feedback file.
    """
    # Read the article
    with open(article_path, 'r', encoding='utf-8') as f:
        article_text = f.read()
    
    # Read the transcript
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_text = f.read()
    
    return review_article(article_text, transcript_text, output_path)

if __name__ == "__main__":
    # Test the agent
    test_article_path = "test_perspective_with_references.txt"
    test_transcript_path = "test_transcript.txt"
    test_output_path = "test_review_feedback.json"
    
    # Create a test article file if it doesn't exist
    if not os.path.exists(test_article_path):
        with open(test_article_path, 'w', encoding='utf-8') as f:
            f.write("This is a test perspective article with references.")
    
    # Create a test transcript file if it doesn't exist
    if not os.path.exists(test_transcript_path):
        with open(test_transcript_path, 'w', encoding='utf-8') as f:
            f.write("This is a test transcript for the perspective article.")
    
    run_article_review_agent(test_article_path, test_transcript_path, test_output_path)
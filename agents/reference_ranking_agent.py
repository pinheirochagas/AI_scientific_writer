import os
import json
from openai import AzureOpenAI
from typing import Dict, Any, List
from schema import StudyExtractionResult

def extract_and_rank_references(manuscript_text: str, references_json: List[Dict[str, Any]], output_path: str) -> str:
    """
    Extract key sentences about Maria Luisa Gorno-Tempini's work from the manuscript and
    rank the most appropriate references from the PubMed search results.
    
    Args:
        manuscript_text: The manuscript text to analyze
        references_json: List of references from PubMed search results
        output_path: Path to save the extracted sentences with ranked references
        
    Returns:
        Path to the saved file with extracted sentences and ranked references
    """
    client = AzureOpenAI(
        api_key=os.environ["VERSA_OPENAI_API_KEY"],
        api_version=os.environ['VERSA_API_VERSION'],
        azure_endpoint=os.environ['VERSA_RESOURCE_ENDPOINT']
    )
    
    # Convert references to string for prompt
    references_str = json.dumps(references_json, indent=2)
    
    
    prompt = f"""
    You will analyze a manuscript text authored by Maria Luisa Gorno-Tempini (written in first person) to identify ALL key sentences about her work and research findings in the field of primary progressive aphasia and related language disorders. For each key sentence you identify, select the most appropriate references from the provided JSON file that best support that sentence.

    For each key sentence, you MUST:
    1. Extract the EXACT verbatim sentence from the manuscript without any modifications
    2. Rank up to 3 references from the provided JSON that best support this sentence - include only the most relevant references
    3. Format each reference in APA style for in-text citation and for the reference list

    Here is the manuscript text to analyze:
    
    {manuscript_text}
    
    Here are the available references (JSON format):
    
    {references_str}

    IMPORTANT REQUIREMENTS:
    1. Be THOROUGH and COMPREHENSIVE - extract ALL significant claims, findings, and research statements throughout the entire 7-page manuscript
    2. Since this is authored by Gorno-Tempini herself, look for sentences where she describes research findings, methodologies, discoveries, or conclusions about PPA and related disorders
    3. Include up to a MAXIMUM of 3 references per sentence, but use fewer (even just 1) if one reference is clearly the best match
    4. Make sure your JSON response is properly formatted and can be parsed
    5. Copy the sentences EXACTLY as they appear in the manuscript - do not paraphrase or modify them in any way
    6. Pay attention to statements about neuroanatomical correlates, variant classifications, diagnostic criteria, imaging findings, and treatment approaches related to PPA
    7. All references must come from the provided JSON file
    8. Format your output as JSON that follows the schema I've provided
    9. Do not limit your extraction to a small number of sentences - be comprehensive and capture ALL significant research statements throughout the paper
    """
    
    print("Extracting sentences about Gorno-Tempini's work and ranking references")
    
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06", #"o1-mini-2024-09-12",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format=StudyExtractionResult
        )
            
        result_json = response.choices[0].message.content
        
        # Parse the JSON - should be valid due to response_format enforcement
        result_dict = json.loads(result_json)
        
        # Validate with our Pydantic schema for extra safety
        extraction_result = StudyExtractionResult(**result_dict)
        
        # Save the validated result
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(extraction_result.model_dump(), indent=2))
            
        print(f"Extracted sentences and ranked references saved to {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Error: {e}")
        
        # Save the raw output in case of error for debugging
        error_path = f"{output_path}.error"
        try:
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(result_json if 'result_json' in locals() else str(e))
            print(f"Error output saved to {error_path}")
        except:
            print("Could not save error output")
        
        return None

def run_reference_ranking_agent(manuscript_path: str, references_json_path: str, output_path: str) -> str:
    """
    Run the reference ranking agent.
    
    Args:
        manuscript_path: Path to the manuscript to analyze
        references_json_path: Path to the JSON file with references
        output_path: Path to save the extracted sentences with ranked references
        
    Returns:
        Path to the saved file with extracted sentences and ranked references
    """
    # Read the manuscript
    with open(manuscript_path, 'r', encoding='utf-8') as f:
        manuscript_text = f.read()
    
    # Read the references JSON
    with open(references_json_path, 'r', encoding='utf-8') as f:
        references_json = json.load(f)
    
    return extract_and_rank_references(manuscript_text, references_json, output_path)

if __name__ == "__main__":
    # Test the agent
    test_manuscript_path = "test_manuscript.txt"
    test_references_json_path = "data/pubmed/search_results.json"
    test_output_path = "test_gorno_tempini_references.json"
    
    # Create a test manuscript if it doesn't exist
    if not os.path.exists(test_manuscript_path):
        with open(test_manuscript_path, 'w', encoding='utf-8') as f:
            f.write("""
            Primary Progressive Aphasia (PPA) is a neurodegenerative syndrome characterized by progressive language impairment. 
            Gorno-Tempini and colleagues identified three main variants of PPA: the nonfluent/agrammatic variant, the semantic variant, and the logopenic variant, each with specific linguistic deficits and neuroanatomical correlates.
            Studies have shown that the logopenic variant of PPA is often associated with underlying Alzheimer's disease pathology, as demonstrated by Gorno-Tempini's research using amyloid imaging.
            The nonfluent variant of PPA, characterized by apraxia of speech and agrammatism, has been linked to atrophy in the left inferior frontal regions and insula in multiple studies by Gorno-Tempini's research group.
            """)
    
    run_reference_ranking_agent(test_manuscript_path, test_references_json_path, test_output_path) 
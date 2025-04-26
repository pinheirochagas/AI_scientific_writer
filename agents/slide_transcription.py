#%%
import io
import base64
import json
import os
import pandas as pd
import pdf2image
from openai import AzureOpenAI
from dotenv import load_dotenv


#%% Load environment variables
load_dotenv('.env', override=True)  # Use override=True to force overwriting

#%% Define dirs

pdf_path = "/Users/pinheirochagas/Documents/ppa_marilu_ai/boon_lead_ppt.pdf"

#%% Convert PDF to images
def pdf_to_images(pdf_path, dpi=300):
    """Convert PDF to images with specified DPI for better quality"""
    return pdf2image.convert_from_path(pdf_path, dpi=dpi)

# You can adjust the DPI based on your needs (higher = better quality but larger files)
pdf_images = pdf_to_images(pdf_path, dpi=300)
pdf_images_df = pd.DataFrame({'images': pdf_images})

#%% Encode an image to base64
def encode_image(image, quality=100):
    """Encode image to base64 with specified quality"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG", quality=quality)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

#%% Define LLM client
client = AzureOpenAI(
        api_key=os.getenv("VERSA_OPENAI_API_KEY"),
        api_version=os.getenv("VERSA_API_VERSION"),
        azure_endpoint=os.getenv("VERSA_RESOURCE_ENDPOINT")
    )
#%%
# import boon_lead.json as dictionary
with open("boon_lead.json", "r") as f:
    boon_lead_contexts = json.load(f)

#%% Process each slide with context
results = []


for i, image in enumerate(pdf_images):
    slide_number = i + 1
    
    # Find the matching context for this slide
    slide_context = None
    for context in boon_lead_contexts:
        if context['slide'] == slide_number:
            slide_context = context['content']
            break
    
    if not slide_context:
        print(f"Warning: No context found for slide {slide_number}")
        slide_context = "No context available for this slide."
    
    # Encode the image
    base64_image = encode_image(image)
    
    # Prepare the message for the LLM
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": f"This is slide {slide_number} from a scientific presentation about linguistic variations and Primary Progressive Aphasia. Please transcribe the content of this slide accurately. Here is some context about this slide that may help you:\n\nCONTEXT: {slide_context}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    # Call the LLM
    print(f"Processing slide {slide_number}...")
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=messages,
        max_tokens=1000
    )
    
    # Extract and save the result
    transcript = response.choices[0].message.content
    
    # Store result
    result = {
        "slide": slide_number,
        "context": slide_context,
        "transcript": transcript
    }
    results.append(result)
    
    print(f"Completed slide {slide_number}")

#%% Save all results
with open("slide_transcriptions.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Completed processing {len(results)} slides. Results saved to slide_transcriptions.json")
# %%

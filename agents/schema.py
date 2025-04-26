from pydantic import BaseModel, Field
from typing import List, Optional

class ReferenceAPA(BaseModel):
    """Represents a single reference formatted in APA style."""
    citation_key: Optional[str] = Field(
        default=None,
        description="Optional unique key/identifier from the original citation list."
    )
    in_text: str = Field(
        ...,
        description="APA style in-text citation (e.g., '(Smith, 2023)' or 'Smith (2023)')."
    )
    full_reference: str = Field(
        ...,
        description="APA style full reference list entry (e.g., 'Smith, J. (2023). Title of the article. Journal Name, 1(2), 34-56.')."
    )

class KeySentenceExtraction(BaseModel):
    """
    Schema for a key sentence extracted from a study and its
    top 3 APA-formatted references.
    """
    verbatim_context: str = Field(
        ...,
        description="The verbatim key sentence extracted from the study."
    )
    references: List[ReferenceAPA] = Field(
        ...,
        description="List containing the top 3 most appropriate references for the key sentence, formatted in APA style."
    )

class StudyExtractionResult(BaseModel):
    """
    Container model for multiple key sentences extracted from a study,
    each with their associated references.
    """
    key_sentences: List[KeySentenceExtraction] = Field(
        ...,
        description="List of key sentences extracted from the study, each with its top 3 references."
    )

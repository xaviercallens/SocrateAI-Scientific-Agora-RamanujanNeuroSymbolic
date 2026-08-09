from pydantic import BaseModel, Field
from typing import Optional, List

class ManuscriptExtraction(BaseModel):
    """Structured output schema for multimodal extraction of Ramanujan manuscripts."""
    raw_latex: str = Field(description="The exact LaTeX representation of the mathematical expressions found in the image.")
    q_series_coefficients: Optional[List[float]] = Field(default=None, description="If a q-series or power series is present, the first 20 extracted coefficients. Null otherwise.")
    archetype_hint: str = Field(description="A brief hint indicating the type of mathematics (e.g., 'Mock Theta Function', 'Continued Fraction').")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0 that the extraction is accurate.")

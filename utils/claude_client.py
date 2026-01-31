"""Claude API client for RFP analysis."""

import json
from typing import Dict, Any
import anthropic


class ClaudeRFPClient:
    """Client for interacting with Claude API for RFP analysis."""
    
    def __init__(self, api_key: str):
        """
        Initialize Claude client.
        
        Args:
            api_key: Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_rfp(self, pdf_base64: str, prompt: str) -> Dict[str, Any]:
        """
        Send PDF to Claude with document vision capability.
        
        Args:
            pdf_base64: Base64-encoded PDF string
            prompt: Analysis prompt with instructions
        
        Returns:
            Parsed JSON dictionary with analysis results
        
        Raises:
            Exception: If API call fails or response cannot be parsed
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=16000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            # Extract text response
            response_text = message.content[0].text
            
            # Parse JSON response
            analysis = self._parse_json_response(response_text)
            
            return analysis
        
        except anthropic.APIError as e:
            raise Exception(f"Claude API error: {str(e)}")
        except anthropic.APITimeoutError:
            raise Exception("Request timed out. Please try again.")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Claude response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error during RFP analysis: {str(e)}")
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from Claude's response, handling markdown code blocks.
        
        Args:
            response_text: Raw text response from Claude
        
        Returns:
            Parsed JSON dictionary
        """
        # Try direct JSON parse first
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Try extracting JSON from markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
            return json.loads(json_str)
        
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
            return json.loads(json_str)
        
        # Last resort: try to find JSON object in text
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start != -1 and end > start:
            json_str = response_text[start:end]
            return json.loads(json_str)
        
        raise json.JSONDecodeError(
            "Could not find valid JSON in response",
            response_text,
            0
        )
    
    def validate_analysis_structure(self, analysis: Dict[str, Any]) -> bool:
        """
        Validate that analysis has required fields.
        
        Args:
            analysis: Parsed analysis dictionary
        
        Returns:
            True if valid, raises Exception if invalid
        """
        required_fields = [
            "client_problems",
            "requirements",
            "gotchas",
            "timeline",
            "next_steps",
            "alignment_questions"
        ]
        
        missing_fields = [f for f in required_fields if f not in analysis]
        
        if missing_fields:
            raise Exception(
                f"Analysis missing required fields: {', '.join(missing_fields)}"
            )
        
        return True

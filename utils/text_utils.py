import json
from typing import Optional

def clean_json_string(text: str) -> str:
    """Clean JSON string by removing markdown code block markers and whitespace."""
    if isinstance(text, dict):
        return text
    if isinstance(text, str):
        if text.startswith("```json"):
            text = text.replace("```json", "", 1)
        if text.endswith("```"):
            text = text.replace("```", "", 1)
        return text.strip()
    return text

def extract_json_from_text(text: str) -> Optional[dict]:
    """
    Extract the first valid JSON object from a text string that might contain
    additional text before or after the JSON block.
    
    Args:
        text (str): Text that might contain a JSON object
        
    Returns:
        Optional[dict]: The extracted JSON object, or None if no valid JSON found
    """
    if isinstance(text, dict):
        return text
        
    if not isinstance(text, str):
        return None
        
    try:
        # Find the first occurrence of a JSON object
        start_idx = text.find('{')
        if start_idx == -1:
            return None
            
        # Find the matching closing brace
        brace_count = 0
        end_idx = -1
        for i in range(start_idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
                    
        if end_idx == -1:
            return None
            
        # Extract just the JSON part and clean it
        json_content = text[start_idx:end_idx]
        cleaned_content = clean_json_string(json_content)
        return json.loads(cleaned_content)
        
    except json.JSONDecodeError:
        return None 
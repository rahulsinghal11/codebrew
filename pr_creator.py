import os
import json
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Suggestion:
    commit_msg: str
    new_code: str
    start_line: int
    end_line: int
    file_path: str
    new_branch: str

def load_suggestion(file_path: str) -> Suggestion:
    """Load a suggestion from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Suggestion file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Raw file content: {content}")  # Debug print
            data = json.loads(content)
            
            # Validate required fields
            required_fields = ['COMMIT_MSG', 'NEW_CODE', 'START_LINE', 'END_LINE', 'FILE_PATH', 'NEW_BRANCH']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
            
            return Suggestion(
                commit_msg=data['COMMIT_MSG'],
                new_code=data['NEW_CODE'],
                start_line=data['START_LINE'],
                end_line=data['END_LINE'],
                file_path=data['FILE_PATH'],
                new_branch=data['NEW_BRANCH']
            )
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error loading {file_path}: {str(e)}")
        raise

def process_suggestions(suggestions_dir: str) -> List[Suggestion]:
    """Process all suggestion files in the directory."""
    suggestions = []
    
    # Get the absolute path of the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    suggestions_path = os.path.join(script_dir, suggestions_dir)
    
    print(f"Script directory: {script_dir}")
    print(f"Looking for suggestions in: {suggestions_path}")
    
    # Create directory if it doesn't exist
    if not os.path.exists(suggestions_path):
        os.makedirs(suggestions_path)
        print(f"Created directory: {suggestions_path}")
    
    # List all files in directory with full paths
    all_files = [os.path.join(suggestions_path, f) for f in os.listdir(suggestions_path)]
    print("\nAll files in directory:")
    for f in all_files:
        print(f"- {f}")
    
    # List all JSON files in the directory
    json_files = [f for f in all_files if f.endswith('.json')]
    print(f"\nFound {len(json_files)} JSON files:")
    for f in json_files:
        print(f"- {f}")
    
    if not json_files:
        print(f"No JSON files found in {suggestions_path}")
        return suggestions
    
    for file_path in json_files:
        try:
            suggestion = load_suggestion(file_path)
            suggestions.append(suggestion)
            print(f"Loaded suggestion from {file_path}")
        except Exception as e:
            print(f"Error loading suggestion from {file_path}: {str(e)}")
    
    return suggestions

def create_pr(suggestion: Suggestion) -> None:
    """Create a PR for a given suggestion."""
    print(f"\nProcessing PR for {suggestion.file_path}")
    print(f"Branch: {suggestion.new_branch}")
    print(f"Commit Message: {suggestion.commit_msg}")
    print(f"Changes in lines {suggestion.start_line}-{suggestion.end_line}")
    print("New Code:")
    print(suggestion.new_code)
    print("-" * 50)

def main():
    suggestions_dir = "suggestions"
    suggestions = process_suggestions(suggestions_dir)
    
    if not suggestions:
        print("No suggestions found to process")
        return
    
    print(f"\nFound {len(suggestions)} suggestions to process")
    
    for suggestion in suggestions:
        create_pr(suggestion)

if __name__ == "__main__":
    main() 
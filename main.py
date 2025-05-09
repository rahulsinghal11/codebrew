import os
from dotenv import load_dotenv
from ai.analyzer import analyze_file

# Load environment variables
load_dotenv()

def main():
    print("🔍 Analyzing sample.py...")
    result = analyze_file("sample.py")

    if result:
        print("\n✅ Suggestion received:")
        print("Issue:", result.get("issue"))
        print("\nOld Code:\n", result.get("old_code"))
        print("\nNew Code:\n", result.get("new_code"))
        print("\nBenefit:", result.get("benefit"))
        print("\nCommit Message:", result.get("commit_message"))
    else:
        print("\n❌ No suggestion returned.")

if __name__ == "__main__":
    main() 
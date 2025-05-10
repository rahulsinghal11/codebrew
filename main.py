import os
from dotenv import load_dotenv
from utils.repo_selector import RepoSelector
from ai.analyzer import analyze_repository_structure, analyze_github_files

def main():
    # Load environment variables
    load_dotenv()
    
    # Get number of files to analyze from environment
    n_files = int(os.getenv("N_FILES", "5"))
    
    # Initialize repository selector
    selector = RepoSelector()
    
    # Get repository info and structure
    repo_info = selector.analyze_repository(n_files)
    if not repo_info:
        print("Failed to get repository information")
        return
        
    # Get Bedrock's analysis of which files to analyze
    selected_files = analyze_repository_structure(repo_info)
    if not selected_files:
        print("Failed to analyze repository structure")
        return
        
    print(f"\n🔍 Selected {len(selected_files)} files for analysis:")
    for file in selected_files:
        print(f"\n📄 {file['name']}")
        print(f"Reason: {file['reason']}")
    
    # Analyze all selected files at once
    print("\n🔍 Analyzing files...")
    analyses = analyze_github_files(selected_files)
    
    if analyses:
        print(f"\n✅ Successfully analyzed {len(analyses)} files")
        if isinstance(analyses, list):
            for analysis in analyses:
                print(f"\n📝 Analysis for {analysis.get('file', 'unknown')}:" )
                print(f"Issue: {analysis.get('issue', '')}")
                print(f"Benefit: {analysis.get('benefit', '')}")
                print(f"Old code:\n{analysis.get('old_code', '')}")
                print(f"New code:\n{analysis.get('new_code', '')}")
                print(f"Commit message: {analysis.get('commit_message', '')}")
                print(f"Branch name: {analysis.get('branch_name', '')}")
        elif isinstance(analyses, dict):
            analysis = analyses
            print(f"\n📝 Analysis for {analysis.get('file', 'unknown')}:" )
            print(f"Issue: {analysis.get('issue', '')}")
            print(f"Benefit: {analysis.get('benefit', '')}")
            print(f"Old code:\n{analysis.get('old_code', '')}")
            print(f"New code:\n{analysis.get('new_code', '')}")
            print(f"Commit message: {analysis.get('commit_message', '')}")
            print(f"Branch name: {analysis.get('branch_name', '')}")
        else:
            print("❌ Unexpected format for analyses:", type(analyses), analyses)
    else:
        print("\n❌ Analysis failed")
            
    print("\n✨ Analysis complete!")

if __name__ == "__main__":
    main() 
# CodeBrew: AI-Powered GitHub Repo Analyzer, Suggestion, and Automation Platform

![CodeBrew Logo](https://img.shields.io/badge/AI%20Code%20Review-Automated-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

---

## 🚀 Overview

**CodeBrew** is an advanced AI-powered platform that automatically selects random GitHub repositories from a configured list, fetches their code using the GitHub API, analyzes them for improvements, and automates the process of creating pull requests and sending email digests. It is designed for teams and individuals who want to supercharge their code quality, automate code reviews, and streamline the process of applying best practices across multiple repositories.

---

## ✨ Features

- **Random GitHub Repo Selection:**  
  Automatically selects repositories from `data/repositories.txt` or `data/repo_urls.txt` for analysis.
- **AI Code Analysis:**  
  Uses AWS Bedrock (Claude 3) to analyze code for performance, readability, best practices, and SQL/import optimizations.
- **Actionable Suggestions:**  
  Generates detailed, context-aware suggestions with before/after code, benefit explanations, and commit messages.
- **Automated Email Digests:**  
  Sends beautiful, HTML-formatted emails with improvement details, code diffs, and a "Create PR" button.
- **One-Click PR Automation:**  
  FastAPI backend lets you create a GitHub pull request with the suggested change in one click.
- **Branch & File Automation:**  
  Automatically creates branches, updates files, commits changes, and opens PRs on GitHub using the GitHub REST API.
- **Suggestion Logging:**  
  All suggestions and PRs are logged for audit and tracking.
- **Multi-Repo Support:**  
  Analyze any public or private GitHub repository (with access).
- **Secure & Configurable:**  
  Uses `.env` for all secrets and supports AWS, GitHub, and SMTP integrations.
- **Extensible & Cross-Platform:**  
  Easily add new analysis logic, email templates, or endpoints. Works on Windows, Mac, and Linux.

---

## 🏗️ Project Structure

```
.
├── ai/                  # AI analyzer and Bedrock client
├── data/                # Suggestions, repo lists, and sample data
│   ├── repositories.txt # List of GitHub repos to analyze
│   ├── repo_urls.txt    # Alternative repo list (one per line)
│   └── suggestions/     # Saved suggestions (JSON) - must exist!
├── utils/               # Email, PR, GitHub, and text utilities
├── web/                 # FastAPI backend for PR automation
├── test_files/          # Example files for testing
├── main.py              # Entry point for orchestrating analysis
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
└── README.md            # This file
```

---

## ⚡ Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/codebrew.git
cd codebrew
```

### 2. Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# Or: source .venv/bin/activate  # On Mac/Linux

pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```env
# AWS (for Bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Bedrock Model
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=1000
BEDROCK_TEMPERATURE=0.1

# GitHub
GITHUB_TOKEN=your_github_pat  # Must have repo access for private repos

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAIL=your-email@gmail.com

# App
SUGGESTIONS_DIR=data/suggestions
```

### 4. Configure Repositories to Analyze

- Add GitHub repository URLs (one per line) to `data/repositories.txt` or `data/repo_urls.txt`.
- The system will randomly select from these for analysis.

---

## 🧠 How It Works

1. **Random Repo Selection:**  
   The system randomly selects a GitHub repository from your configured list.
2. **Fetch & Analyze:**  
   It fetches code files from the selected repo using the GitHub API and uses AI to analyze them for high-impact, safe, and local improvements.
3. **Save Suggestion:**  
   Suggestions are saved as JSON in `data/suggestions/`.
4. **Email Notification:**  
   An HTML email is sent with the improvement, code diff, and a "Create PR" button.
5. **Create PR:**  
   Clicking the button calls a FastAPI endpoint, which:
   - Creates a new branch from the base (via GitHub API)
   - Updates the file with the improved code (via GitHub API)
   - Commits and pushes the change (via GitHub API)
   - Opens a pull request on GitHub (via GitHub API)

---

## 🛠️ Usage

### Run the Analyzer (Random Repo Selection)

```bash
python main.py
```

- This will randomly select a repo, fetch its code, analyze it, and generate a suggestion.

### Run the FastAPI Server

```bash
.venv\Scripts\python.exe -m uvicorn web.pr_api:app --reload --port 8000
```

- The FastAPI backend exposes endpoints (e.g., `/create_pr`) for PR automation, which can be triggered from email links or directly via HTTP requests.

### Send a Test Email

```bash
python test_email.py
```

### Create a PR from a Suggestion

Visit the link in your email or call the endpoint directly:

```
GET /create_pr?repo_name=owner/repo&owner=owner&base_branch=main
```

---

## 📬 Email Example

- **Improvement details** (issue, benefit, commit message)
- **Before/After code** (with preserved formatting)
- **"Create PR" button** (one-click automation)
- **Repository and file context**

---

## 🔌 Integrations

- **AWS Bedrock:** For AI code analysis (Claude 3)
- **GitHub REST API:** For fetching code, creating branches, updating files, and making PRs
- **SMTP:** For sending notification emails

---

## 🧩 Extending & Customizing

- Add new prompt templates in `prompts/`
- Customize email templates in `utils/emailer.py`
- Add new FastAPI endpoints in `web/pr_api.py`
- Add more code analysis logic in `ai/analyzer.py`
- Works on Windows, Mac, and Linux

---

## 🛡️ Security & Best Practices

- **Never commit your `.env` file.**
- Use least-privilege AWS and GitHub tokens.
- Use app-specific passwords for email.
- Regularly rotate credentials.

---

## 🛠️ Troubleshooting

- **ModuleNotFoundError:**
  - Ensure all dependencies are installed: `pip install -r requirements.txt`
  - If you see `No module named 'dotenv'` or `No module named 'uvicorn'`, install them manually.
- **FileNotFoundError:**
  - Make sure the `data/suggestions/` directory exists before running the analyzer or server.
- **Permission Errors:**
  - Your GitHub token must have `repo` access for private repositories.
  - AWS and SMTP credentials must be valid and active.
- **API Rate Limits:**
  - The GitHub API has rate limits. Use a personal access token to increase your quota.
- **Cross-Platform:**
  - All scripts and tools are designed to work on Windows, Mac, and Linux.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit and push your changes
4. Open a Pull Request

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 👥 Authors & Credits

- **Rahul Singhal**
- **Priyanshu Jaiswal**
- **Pratham Patel**
- **Aman Sachdeva**

---

## 💡 Example Suggestion JSON

```json
{
  "issue": "Inefficient nested loops to find duplicates",
  "repo_name": "codebrew",
  "file_path": "src/utils/duplicate_finder.py",
  "file_name": "duplicate_finder.py",
  "start_line": 10,
  "end_line": 15,
  "old_code": "    for i in range(len(arr)):\n        for j in range(i+1, len(arr)):\n            if arr[i] == arr[j]:\n                duplicates.append(arr[i])",
  "new_code": "    seen = set()\n    for item in arr:\n        if item in seen:\n            duplicates.append(item)\n        seen.add(item)",
  "benefit": "Reduces time complexity from O(n^2) to O(n); ~80% faster on large inputs.",
  "commit_message": "Optimize duplicate search with set lookup",
  "branch_name": "optimize-duplicate-search"
}
```

---

## 🧑‍💻 Support

For questions, issues, or feature requests, please open an issue on GitHub. 
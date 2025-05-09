from flask import Flask, render_template, request, jsonify
from pathlib import Path
import sys

# Add parent directory to path to import from sibling packages
sys.path.append(str(Path(__file__).parent.parent))

from ai.analyzer import CodeAnalyzer
from utils.pr_creator import PRCreator
from utils.emailer import Emailer

app = Flask(__name__)
analyzer = CodeAnalyzer()
pr_creator = PRCreator()
emailer = Emailer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_code():
    code = request.json.get('code')
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    analysis = analyzer.analyze_code(code)
    return jsonify(analysis)

@app.route('/create-pr', methods=['POST'])
def create_pr():
    data = request.json
    required = ['repo', 'title', 'body', 'branch']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = pr_creator.create_pull_request(
        repo_name=data['repo'],
        title=data['title'],
        body=data['body'],
        head_branch=data['branch']
    )
    return jsonify(result)

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.json
    required = ['email', 'subject', 'message']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = emailer.send_email(
        to_email=data['email'],
        subject=data['subject'],
        body=data['message']
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 
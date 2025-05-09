# CodeBrew - AI Code Analyzer

An AI-powered code analyzer that provides actionable suggestions for improving your Python codebase.

## Features

- Analyzes Python code for potential improvements
- Suggests optimizations for performance, readability, and best practices
- Identifies SQL query optimizations
- Recommends import optimizations
- Generates detailed improvement suggestions with benefits
- Saves suggestions in JSON format

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/codebrew.git
cd codebrew
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following configuration:
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Bedrock Model Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=1000
BEDROCK_TEMPERATURE=0.1

# Application Configuration
SUGGESTIONS_DIR=data/suggestions
```

## Usage

Analyze a Python file:
```bash
python main.py path/to/your/file.py
```

The analyzer will:
1. Read and analyze the specified file
2. Generate improvement suggestions
3. Save suggestions in JSON format
4. Display the analysis results in the console

## Configuration

### AWS Configuration
- `AWS_REGION`: AWS region for Bedrock service
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

### Bedrock Model Configuration
- `BEDROCK_MODEL_ID`: ID of the Bedrock model to use
- `BEDROCK_MAX_TOKENS`: Maximum tokens for model response
- `BEDROCK_TEMPERATURE`: Model temperature (0.0-1.0)

### Application Configuration
- `SUGGESTIONS_DIR`: Directory to save suggestion files

## Security Notes

1. Never commit your `.env` file to version control
2. Keep your AWS credentials secure
3. Use IAM roles with minimal required permissions
4. Regularly rotate your AWS access keys

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 
# CodeBrew

A Python project with AI, web, and data processing capabilities.

## Project Structure

```
codebrew/
├── ai/         # AI-related code
├── utils/      # Utility functions
├── web/        # Web-related code
├── data/       # Data storage and processing
├── main.py     # Main application entry point
└── requirements.txt
```

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd codebrew
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your environment variables:
```
ENV=development
DEBUG=True
```

5. Run the application:
```bash
python main.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
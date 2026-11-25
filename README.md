# AI-Powered DevOps Incident Assistant

An AI-powered web application that helps DevOps engineers analyze infrastructure errors, understand possible root causes, and find troubleshooting steps.

## Project Overview

The AI-Powered DevOps Incident Assistant is designed to simplify the initial investigation of common DevOps incidents. Users can enter an error log, select an environment, and receive an explanation with possible causes, suggested solutions, and useful commands.

The application uses Google Gemini AI for intelligent analysis and a rule-based fallback when the AI service is unavailable.

## Features

- Analyze infrastructure error logs.
- Support for Kubernetes, Docker, AWS, Linux, Networking, and other environments.
- Identify incident severity.
- Suggest possible root causes.
- Provide troubleshooting steps and commands.
- Gemini AI integration.
- Rule-based fallback for service availability.
- Dashboard with incident history.

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- Google Gemini API
- Python dotenv

## Project Structure

```text
ai-devops-incident-assistant/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/shreyagarg7188-hue/ai-devops-incident-assistant.git
cd ai-devops-incident-assistant
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Replace the placeholder with your own Google Gemini API key. Never share or commit your API key.

### 5. Run the application

```bash
python3 app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## Example Use Case

**Environment:** Kubernetes

**Input:** Pod is in CrashLoopBackOff state.

**Expected analysis:**
- Incident identification
- Severity assessment
- Possible root cause
- Troubleshooting suggestions
- Useful Kubernetes commands

## Important Note

This tool analyzes user-provided logs and provides troubleshooting guidance. It does not directly access or modify live cloud infrastructure, servers, containers, or Kubernetes clusters.

## Future Improvements

- Persistent incident history using a database.
- User authentication.
- More DevOps incident patterns.
- Integration with monitoring and alerting platforms.
- Deployment on a cloud platform.

## Author

Developed as an AI-powered DevOps project to simplify infrastructure incident analysis and troubleshooting.

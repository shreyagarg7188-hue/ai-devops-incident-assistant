
import os
import json
import time

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

client = genai.Client(api_key=API_KEY) if API_KEY else None


# --------------------------------
# AI-POWERED INCIDENT ANALYSIS
# --------------------------------

def analyze_with_ai(log, environment):

    prompt = f"""
You are an experienced DevOps incident analysis assistant.

Analyze the following technical error.

Environment: {environment}
Error Log: {log}

Instructions:
1. Identify the technical issue.
2. Assign severity: Critical, High, Medium or Low.
3. Explain possible root cause.
4. Provide 3 to 5 troubleshooting steps.
5. Suggest relevant commands.
6. Never claim you accessed the actual server.
7. Clearly mention uncertainty.
8. Explain risks of destructive commands.

Return ONLY valid JSON:

{{
    "issue": "Short issue name",
    "severity": "High",
    "root_cause": "Possible explanation",
    "solutions": ["Step 1", "Step 2", "Step 3"],
    "commands": ["command 1", "command 2"],
    "ai_analysis": "Additional explanation"
}}
"""

    response = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )
            break

        except errors.ServerError:
            if attempt == 2:
                raise

            time.sleep(2 ** (attempt + 1))

    if response is None or not response.text:
        raise ValueError("Empty response from Gemini API")

    text = response.text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    result = json.loads(text)

    required_fields = [
        "issue", "severity", "root_cause",
        "solutions", "commands", "ai_analysis"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError("AI returned incomplete analysis")

    if result["severity"] not in ["Critical", "High", "Medium", "Low"]:
        result["severity"] = "Medium"

    result["analysis_type"] = "Gemini AI"

    return result


# --------------------------------
# RULE-BASED FALLBACK ANALYSIS
# --------------------------------

def analyze_with_rules(log, environment):

    text = log.lower()

    if "crashloopbackoff" in text:

        return {
            "issue": "Kubernetes CrashLoopBackOff",
            "severity": "High",
            "root_cause": "Container is repeatedly restarting.",
            "solutions": [
                "Check previous container logs.",
                "Describe the affected pod.",
                "Verify environment variables and configuration.",
                "Inspect resource limits and health probes."
            ],
            "commands": [
                "kubectl get pods",
                "kubectl describe pod <pod-name>",
                "kubectl logs <pod-name> --previous"
            ],
            "ai_analysis": "Rule-based diagnostic fallback. Actual Kubernetes cluster was not accessed.",
            "analysis_type": "Rule-based fallback"
        }

    elif "port is already allocated" in text or "address already in use" in text:

        return {
            "issue": "Docker Port Conflict",
            "severity": "Medium",
            "root_cause": "Another process may be using the requested port.",
            "solutions": [
                "Identify the process using the port.",
                "Check running Docker containers.",
                "Choose another available host port."
            ],
            "commands": [
                "docker ps -a",
                "lsof -i :8080",
                "docker run -p 8081:8080 <image>"
            ],
            "ai_analysis": "Rule-based diagnostic fallback. Host processes were not inspected.",
            "analysis_type": "Rule-based fallback"
        }

    elif "accessdenied" in text or "not authorized" in text:

        return {
            "issue": "AWS IAM Access Denied",
            "severity": "High",
            "root_cause": "IAM identity may lack required EC2 permissions or an applicable policy may deny the action.",
            "solutions": [
                "Identify the IAM user or role making the request.",
                "Review attached IAM policies.",
                "Check permissions boundaries and service control policies.",
                "Check resource restrictions and explicit denies.",
                "Grant only the minimum required permissions after verification."
            ],
            "commands": [
                "aws sts get-caller-identity",
                "aws iam simulate-principal-policy --policy-source-arn <arn> --action-names ec2:RunInstances"
            ],
            "ai_analysis": "Rule-based diagnostic fallback. AWS account was not accessed.",
            "analysis_type": "Rule-based fallback"
        }

    elif "permission denied" in text:

        return {
            "issue": "Linux Permission Denied",
            "severity": "Medium",
            "root_cause": "Current user may lack required file permissions.",
            "solutions": [
                "Inspect file permissions.",
                "Verify file ownership.",
                "Grant execute permission if appropriate."
            ],
            "commands": [
                "ls -l deploy.sh",
                "chmod +x deploy.sh"
            ],
            "ai_analysis": "Rule-based diagnostic fallback. Actual filesystem was not inspected.",
            "analysis_type": "Rule-based fallback"
        }

    else:

        return {
            "issue": f"{environment} Technical Error",
            "severity": "Medium",
            "root_cause": "The log requires further investigation.",
            "solutions": [
                "Review the complete error log.",
                "Check service configuration.",
                "Inspect relevant system logs."
            ],
            "commands": [
                "Check relevant service status and logs."
            ],
            "ai_analysis": "Rule-based fallback. More diagnostic information is required.",
            "analysis_type": "Rule-based fallback"
        }


# --------------------------------
# HOME PAGE
# --------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------
# INCIDENT ANALYSIS API
# --------------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json(silent=True) or {}

        log = data.get("log", "").strip()
        environment = data.get("environment", "Other")

        if not log:
            return jsonify({
                "error": "Please enter an error log"
            }), 400

        if len(log) > 12000:
            return jsonify({
                "error": "Error log is too long"
            }), 400

        allowed_environments = [
            "Kubernetes", "Docker", "AWS",
            "Linux", "Networking", "Other"
        ]

        if environment not in allowed_environments:
            environment = "Other"

        # Try Gemini AI first
        if client:

            try:
                result = analyze_with_ai(log, environment)

            except Exception:
                app.logger.exception(
                    "Gemini unavailable. Switching to rule-based fallback."
                )

                result = analyze_with_rules(log, environment)

        else:

            result = analyze_with_rules(log, environment)

        return jsonify(result)

    except Exception:

        app.logger.exception("Incident analysis failed")

        return jsonify({
            "error": "Incident analysis failed. Please try again."
        }), 500


# --------------------------------
# RUN APPLICATION
# --------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)

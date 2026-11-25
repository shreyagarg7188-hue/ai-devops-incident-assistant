
const form = document.getElementById("analyzeForm");
const errorLog = document.getElementById("errorLog");
const environment = document.getElementById("environment");

const analyzeBtn = document.getElementById("analyzeBtn");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const analysisContent = document.getElementById("analysisContent");

let incidentHistory = [];

form.addEventListener("submit", async function(event) {
    event.preventDefault();

    const log = errorLog.value.trim();

    if (!log) {
        alert("Please enter an error log.");
        return;
    }

    analyzeBtn.disabled = true;
    loading.classList.remove("hidden");
    result.classList.add("hidden");

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                log: log,
                environment: environment.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Analysis failed");
        }

        displayResult(data);

    } catch (error) {
        alert("Error: " + error.message);
    } finally {
        loading.classList.add("hidden");
        analyzeBtn.disabled = false;
    }
});

function displayResult(data) {
    analysisContent.replaceChildren();

    const sections = [
        ["Issue", data.issue],
        ["Severity", data.severity],
        ["Root Cause", data.root_cause],
        ["Recommended Solutions", data.solutions],
        ["Useful Commands", data.commands],
        ["AI Analysis", data.ai_analysis]
    ];

    sections.forEach(([heading, content]) => {
        if (!content) return;

        const section = document.createElement("div");
        const title = document.createElement("h3");
        const paragraph = document.createElement("p");

        title.textContent = heading;
        paragraph.textContent = Array.isArray(content)
            ? content.join("\n")
            : content;

        section.append(title, paragraph);
        section.style.marginBottom = "18px";

        analysisContent.appendChild(section);
    });

    result.classList.remove("hidden");

    incidentHistory.unshift({
        issue: data.issue || "DevOps Incident",
        severity: data.severity || "Unknown"
    });

    updateDashboard();
}

function updateDashboard() {
    document.getElementById("totalIncidents").textContent =
        incidentHistory.length;

    document.getElementById("criticalIncidents").textContent =
        incidentHistory.filter(item =>
            item.severity.toLowerCase() === "critical"
        ).length;

    document.getElementById("todayIncidents").textContent =
        incidentHistory.length;

    const historyList = document.getElementById("historyList");
    historyList.replaceChildren();

    incidentHistory.forEach(item => {
        const div = document.createElement("div");
        div.className = "history-item";

        div.textContent = `${item.issue} — ${item.severity}`;
        historyList.appendChild(div);
    });
}

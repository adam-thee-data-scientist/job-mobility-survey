#"https://docs.google.com/spreadsheets/d/1zXUqSzJP1lqWhKWKTp9-aq1IkvhsAnD63r0x13ewcmU"

from flask import Flask, render_template_string, request
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json


app = Flask(__name__)

# --- [CONFIGURATION] ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zXUqSzJP1lqWhKWKTp9-aq1IkvhsAnD63r0x13ewcmU"
CREDS_FILE = "service_account.json"
LINKEDIN_URL = "https://www.linkedin.com/in/adam-thee-data-scientist/"

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 1. Try to read from the Render Environment Variable first
    creds_json = os.environ.get("GOOGLE_CREDS")
    
    if creds_json:
        # We are on Render: Use the secret environment variable
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    else:
        # We are local: Use the service_account.json file
        creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
        
    client = gspread.authorize(creds)
    return client.open_by_url(SHEET_URL).sheet1

# --- [UI DESIGN] ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Research Portfolio</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 950px; margin: 40px auto; background-color: #f9f9f9; padding: 20px; }
        .card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 30px; }
        h2 { color: #111; margin-bottom: 20px; border-bottom: 2px solid #ef4444; display: inline-block; }
        
        table { width: 100%; border-collapse: collapse; table-layout: fixed; }
        th { font-size: 11px; text-transform: uppercase; color: #666; padding: 10px; text-align: center; }
        th:first-child { width: 45%; text-align: left; font-size: 13px; color: #111; }
        
        td { padding: 15px 5px; border-bottom: 1px solid #eee; }
        .question { font-size: 14px; color: #333; line-height: 1.4; }
        .radio-cell { text-align: center; }
        
        input[type="radio"] { width: 18px; height: 18px; cursor: pointer; accent-color: #ef4444; }
        
        .btn { margin-top: 30px; background: #111; color: white; border: none; padding: 12px 24px; border-radius: 4px; font-weight: 600; cursor: pointer; width: 100%; }
        
        /* Success Message Styling */
        .success-box { background: #111; color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; text-align: center; }
        .success-box a { color: #ef4444; font-weight: bold; text-decoration: none; border-bottom: 1px solid #ef4444; }
        
        .chart-container { position: relative; height: 300px; width: 100%; margin-top: 20px; }
    </style>
</head>
<body>
    {% if success %}
    <div class="success-box">
        <h3>✅ Thank you for contributing to this research!</h3>
        <p>Your perspective helps shape our understanding of AI in the modern workplace.</p>
        <p>Interested in the final report? Let's connect on <a href="{{ linkedin_url }}" target="_blank" rel="noopener noreferrer">LinkedIn</a>.</p>
    </div>
    {% endif %}

    <div class="card">
        <h2>AI Workplace Sentiment Survey</h2>
        <form method="POST">
            <table>
                <thead>
                    <tr>
                        <th>Research Question</th>
                        <th>Strongly Disagree</th>
                        <th>Disagree</th>
                        <th>Neutral</th>
                        <th>Agree</th>
                        <th>Strongly Agree</th>
                    </tr>
                </thead>
                <tbody>
                    {% for q_id, q_text in questions.items() %}
                    <tr>
                        <td class="question">{{ q_text }}</td>
                        {% for i in range(1, 6) %}
                        <td class="radio-cell"><input type="radio" name="{{ q_id }}" value="{{ i }}" required></td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            <button type="submit" class="btn">Submit Response</button>
        </form>
    </div>

    <div class="card">
        <h2>Community Insights</h2>
        <div class="chart-container">
            <canvas id="resultsChart"></canvas>
        </div>
        <p style="text-align: center; font-size: 12px; color: #999; margin-top: 20px;">Total Participants: {{ total }}</p>
    </div>

    <script>
        const ctx = document.getElementById('resultsChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['AI Confidence', 'Skill Relevance', 'Unofficial Use'],
                datasets: [{
                    label: 'Average Score (1-5)',
                    data: [{{ averages['q1'] }}, {{ averages['q2'] }}, {{ averages['q3'] }}],
                    backgroundColor: 'rgba(239, 68, 68, 0.2)',
                    borderColor: '#ef4444',
                    borderWidth: 2,
                    borderRadius: 5
                }]
            },
            options: {
                indexAxis: 'y',
                scales: { x: { min: 1, max: 5 } },
                plugins: { legend: { display: false } },
                maintainAspectRatio: false
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    questions = {
        "q1": "I feel confident identifying when an AI-generated output is factually incorrect.",
        "q2": "My current core technical skills will remain relevant for the next 3 years.",
        "q3": "I use AI for tasks not explicitly part of my official job description."
    }
    success = False
    sheet = get_sheet()

    if request.method == "POST":
        try:
            row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            for q_id in questions.keys():
                row.append(request.form.get(q_id))
            sheet.append_row(row)
            success = True
        except Exception as e:
            return f"Error: {e}"

    all_data = sheet.get_all_values()[1:] 
    total = len(all_data)
    averages = {"q1": 0, "q2": 0, "q3": 0}
    
    if total > 0:
        for q_key, idx in [("q1", 1), ("q2", 2), ("q3", 3)]:
            scores = [int(row[idx]) for row in all_data if row[idx].isdigit()]
            if scores:
                averages[q_key] = round(sum(scores) / len(scores), 2)

    return render_template_string(HTML_TEMPLATE, 
                                 questions=questions, 
                                 success=success, 
                                 averages=averages, 
                                 total=total,
                                 linkedin_url=LINKEDIN_URL)

if __name__ == "__main__":
    app.run(debug=True)
# Powered by Viddertech

import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates a self-contained HTML report for quiz results.
    """

    @staticmethod
    def generate_html_report(quiz_title: str, scores: dict) -> str:
        """
        Takes quiz data and generates a beautiful HTML report.

        :param quiz_title: The title of the quiz.
        :param scores: A dictionary of scores, where keys are user IDs and
                       values are dicts {'name': str, 'score': float}.
        :return: A string containing the full HTML report.
        """

        # Sort scores for the leaderboard
        sorted_scores = sorted(scores.items(), key=lambda item: item[1]['score'], reverse=True)

        # --- Build the table rows for the leaderboard ---
        table_rows_html = ""
        for rank, (user_id, data) in enumerate(sorted_scores, 1):
            trophy = "🏆" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else str(rank)
            name = data.get('name', 'Unknown User')
            score = round(data.get('score', 0), 2)
            table_rows_html += f"""
            <tr>
                <td>{trophy}</td>
                <td>{name}</td>
                <td>{score}</td>
            </tr>
            """

        if not table_rows_html:
            table_rows_html = "<tr><td colspan='3'>No participants in this quiz.</td></tr>"

        # --- HTML Template ---
        # This is a self-contained HTML file with CSS and JS.
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz Report: {quiz_title}</title>
    <style>
        :root {{
            --bg-color-light: #f4f6f8;
            --text-color-light: #1a1a1a;
            --card-bg-light: #ffffff;
            --border-color-light: #e1e4e8;
            --header-bg-light: #007bff;
            --header-text-light: #ffffff;

            --bg-color-dark: #1a1c20;
            --text-color-dark: #e1e1e1;
            --card-bg-dark: #2a2d34;
            --border-color-dark: #3a3d44;
            --header-bg-dark: #1e88e5;
            --header-text-dark: #ffffff;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 20px;
            transition: background-color 0.3s, color 0.3s;
        }}
        .light-theme {{
            background-color: var(--bg-color-light);
            color: var(--text-color-light);
        }}
        .dark-theme {{
            background-color: var(--bg-color-dark);
            color: var(--text-color-dark);
        }}
        .container {{
            max-width: 800px;
            margin: auto;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: background-color 0.3s;
        }}
        .light-theme .container {{
            background-color: var(--card-bg-light);
            border: 1px solid var(--border-color-light);
        }}
        .dark-theme .container {{
            background-color: var(--card-bg-dark);
            border: 1px solid var(--border-color-dark);
        }}
        .header {{
            text-align: center;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            margin: -20px -20px 20px -20px;
        }}
        .light-theme .header {{
            background-color: var(--header-bg-light);
            color: var(--header-text-light);
        }}
        .dark-theme .header {{
            background-color: var(--header-bg-dark);
            color: var(--header-text-dark);
        }}
        h1 {{
            margin: 0;
            font-size: 2em;
        }}
        h2 {{
            margin-top: 30px;
            border-bottom: 2px solid;
            padding-bottom: 10px;
        }}
        .light-theme h2 {{ border-color: var(--header-bg-light); }}
        .dark-theme h2 {{ border-color: var(--header-bg-dark); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid;
        }}
        .light-theme th, .light-theme td {{ border-color: var(--border-color-light); }}
        .dark-theme th, .dark-theme td {{ border-color: var(--border-color-dark); }}

        .light-theme thead {{ background-color: #e9ecef; }}
        .dark-theme thead {{ background-color: #3a3d44; }}

        .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 0.9em;
            opacity: 0.7;
        }}
        .theme-toggle {{
            position: fixed;
            top: 15px;
            right: 15px;
            cursor: pointer;
            font-size: 1.5em;
            border: 1px solid;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .light-theme .theme-toggle {{ border-color: var(--border-color-light); }}
        .dark-theme .theme-toggle {{ border-color: var(--border-color-dark); }}
    </style>
</head>
<body>
    <div class="theme-toggle" onclick="toggleTheme()">☀️</div>

    <div class="container">
        <div class="header">
            <h1>Quiz Report</h1>
            <p>Results for: {quiz_title}</p>
        </div>

        <h2>Leaderboard</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Participant</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>

        <div class="footer">
            <p>Generated by Viddertech Advance Quiz Bot</p>
        </div>
    </div>

    <script>
        const body = document.body;
        const toggleButton = document.querySelector('.theme-toggle');

        function setInitialTheme() {{
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            const savedTheme = localStorage.getItem('theme');

            if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {{
                body.className = 'dark-theme';
                toggleButton.innerHTML = '🌙';
            }} else {{
                body.className = 'light-theme';
                toggleButton.innerHTML = '☀️';
            }}
        }}

        function toggleTheme() {{
            if (body.classList.contains('light-theme')) {{
                body.className = 'dark-theme';
                toggleButton.innerHTML = '🌙';
                localStorage.setItem('theme', 'dark');
            }} else {{
                body.className = 'light-theme';
                toggleButton.innerHTML = '☀️';
                localStorage.setItem('theme', 'light');
            }}
        }}

        document.addEventListener('DOMContentLoaded', setInitialTheme);
    </script>
</body>
</html>
        """
        return html_template
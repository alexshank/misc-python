import csv
import sys
import os


def parse_csv(filepath):
    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        players = []
        for row in reader:
            player = {
                "batting_order": row["Batting Order"],
                "name": row["Player Name"],
                "innings": [row[f"Inning {i}"] for i in range(1, 10)],
            }
            players.append(player)
        return players


def generate_html(players, output_filename="output.html"):
    def generate_inning_field(inning_idx):
        positions = {
            "P": "",
            "C": "",
            "1B": "",
            "2B": "",
            "3B": "",
            "SS": "",
            "LF": "",
            "CF": "",
            "RF": "",
            "RV": "",
        }
        benched = []

        for player in players:
            pos = player["innings"][inning_idx]
            if pos in positions:
                positions[pos] = player["name"]
            else:
                benched.append(player["name"])

        # HTML representation of field layout
        return f"""
        <div class="inning">
            <h2>Inning {inning_idx + 1}</h2>
            <div class="field">
                <div class="position cf">{positions["CF"]}</div>
                <div class="position lf">{positions["LF"]}</div>
                <div class="position rf">{positions["RF"]}</div>
                <div class="position ss">{positions["SS"]}</div>
                <div class="position 2b">{positions["2B"]}</div>
                <div class="position 3b">{positions["3B"]}</div>
                <div class="position 1b">{positions["1B"]}</div>
                <div class="position p">{positions["P"]}</div>
                <div class="position c">{positions["C"]}</div>
                <div class="position rv">{positions["RV"]}</div>
                <div class="bench">
                    <strong>Benched:</strong> {', '.join(benched)}
                </div>
            </div>
        </div>
        """

    # HTML header
    html = """
    <html>
    <head>
        <title>Softball Lineup</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f5f5f5; }
            table { border-collapse: collapse; margin-bottom: 40px; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            .inning { margin-bottom: 60px; }
            .field {
                position: relative;
                width: 500px;
                height: 400px;
                margin: auto;
                background: #d4edda;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 20px;
            }
            .position {
                position: absolute;
                width: 80px;
                text-align: center;
                font-weight: bold;
                background: #fff;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 5px;
            }
            .p   { top: 150px; left: 210px; }
            .c   { top: 270px; left: 210px; }
            .1b  { top: 180px; left: 360px; }
            .2b  { top: 100px; left: 300px; }
            .3b  { top: 100px; left: 120px; }
            .ss  { top: 140px; left: 200px; }
            .lf  { top: 30px; left: 80px; }
            .cf  { top: 20px; left: 210px; }
            .rf  { top: 30px; left: 340px; }
            .rv  { top: 320px; left: 400px; background: #ffeb3b; }
            .bench {
                margin-top: 20px;
                font-style: italic;
                background: #eee;
                padding: 10px;
                border-radius: 6px;
            }
            /* Add styling for position cells in table */
            .position-cell {
                text-align: center;
                font-weight: bold;
            }
            .benched-cell {
                background-color: #ffcccc;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h1>Softball Lineup Summary</h1>
        <h2>Batting Order and Positions by Inning</h2>
        <table>
            <tr>
                <th>Order</th>
                <th>Player</th>
                <th>Inning 1</th>
                <th>Inning 2</th>
                <th>Inning 3</th>
                <th>Inning 4</th>
                <th>Inning 5</th>
                <th>Inning 6</th>
                <th>Inning 7</th>
                <th>Inning 8</th>
                <th>Inning 9</th>
            </tr>
    """

    for player in players:
        html += f"<tr><td>{player['batting_order']}</td><td>{player['name']}</td>"

        # Add cell for each inning with position
        for position in player["innings"]:
            css_class = (
                "benched-cell"
                if position
                not in ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "RV"]
                else "position-cell"
            )
            html += f"<td class='{css_class}'>{position}</td>"

        html += "</tr>"

    html += "</table>"

    for i in range(9):
        html += generate_inning_field(i)

    html += """
    <div style="margin-top: 30px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
        <h3>Legend:</h3>
        <ul>
            <li>P - Pitcher</li>
            <li>C - Catcher</li>
            <li>1B - First Base</li>
            <li>2B - Second Base</li>
            <li>3B - Third Base</li>
            <li>SS - Shortstop</li>
            <li>LF - Left Field</li>
            <li>CF - Center Field</li>
            <li>RF - Right Field</li>
            <li>RV - Rover</li>
        </ul>
        <p>Positions highlighted in red indicate the player is benched for that inning.</p>
    </div>
    </body></html>"""

    with open(output_filename, "w") as f:
        f.write(html)

    print(f"HTML summary saved to {output_filename}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python webpage.py outputs/yourfile.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        sys.exit(1)

    players = parse_csv(csv_path)
    output_dir = "outputs_webpages"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(
        output_dir, os.path.basename(csv_path).replace(".csv", ".html")
    )
    generate_html(players, output_filename)

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

        # HTML representation using CSS grid layout
        return f"""
        <div class="inning">
            <h2>Inning {inning_idx + 1}</h2>
            <div class="field-container">
                <div class="field">
                    <div class="position-area p">{positions["P"] or "P"}</div>
                    <div class="position-area c">{positions["C"] or "C"}</div>
                    <div class="position-area first">{positions["1B"] or "1B"}</div>
                    <div class="position-area second">{positions["2B"] or "2B"}</div>
                    <div class="position-area third">{positions["3B"] or "3B"}</div>
                    <div class="position-area ss">{positions["SS"] or "SS"}</div>
                    <div class="position-area lf">{positions["LF"] or "LF"}</div>
                    <div class="position-area cf">{positions["CF"] or "CF"}</div>
                    <div class="position-area rf">{positions["RF"] or "RF"}</div>
                    <div class="position-area rc">{positions["RV"] or "RC/RV"}</div>
                    <div class="home-plate"></div>
                    <div class="base first-base"></div>
                    <div class="base second-base"></div>
                    <div class="base third-base"></div>
                    <div class="pitchers-mound"></div>
                </div>
                <div class="bench">
                    <strong>Benched:</strong> {', '.join(benched) if benched else 'None'}
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
            
            /* Field container */
            .field-container {
                margin: auto;
                width: 800px;
            }
            
            /* Field grid layout */
            .field {
                display: grid;
                grid-template-columns: repeat(50, 1fr);
                grid-template-rows: repeat(50, 1fr);
                width: 800px;
                height: 800px;
                background: #8bbc84; /* Green grass color */
                position: relative;
                border-radius: 50% 50% 0 0; /* Create the outfield curve */
                border: 2px solid #333;
                margin: 0 auto;
                overflow: hidden;
            }
            
            /* Infield dirt */
            .field:before {
                content: "";
                position: absolute;
                width: 60%;
                height: 60%;
                background: #c2996c; /* Infield dirt color */
                bottom: 0;
                left: 20%;
                clip-path: polygon(50% 0%, 100% 70%, 100% 100%, 0 100%, 0 70%);
            }
            
            /* Common position area styling */
            .position-area {
                background: rgba(255, 255, 255, 0.8);
                border: 2px solid #333;
                border-radius: 8px;
                padding: 5px;
                text-align: center;
                font-weight: bold;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10;
            }
            
            /* Occupied position highlighting */
            .position-area:not(:empty) {
                background: #ffeb3b; /* Yellow highlight for filled positions */
            }
            
            /* Position-specific grid areas */
            .p { grid-area: 30 / 24 / 33 / 27; }
            .c { grid-area: 45 / 24 / 48 / 27; }
            .first { grid-area: 37 / 34 / 40 / 38; }
            .second { grid-area: 27 / 30 / 30 / 34; }
            .third { grid-area: 37 / 16 / 40 / 20; }
            .ss { grid-area: 27 / 20 / 30 / 24; }
            .lf { grid-area: 12 / 10 / 16 / 17; }
            .cf { grid-area: 5 / 22 / 9 / 29; }
            .rf { grid-area: 12 / 33 / 16 / 40; }
            .rc { grid-area: 10 / 27 / 14 / 34; background: rgba(255, 230, 59, 0.8); }
            
            /* Base styling */
            .base {
                width: 20px;
                height: 20px;
                background: white;
                position: absolute;
                transform: rotate(45deg);
                border: 1px solid #333;
                z-index: 5;
            }
            
            .home-plate {
                width: 20px;
                height: 20px;
                background: white;
                position: absolute;
                bottom: 15%;
                left: 50%;
                transform: translateX(-50%);
                clip-path: polygon(0 0, 50% 100%, 100% 0);
                z-index: 5;
            }
            
            .first-base {
                bottom: 40%;
                right: 30%;
            }
            
            .second-base {
                bottom: 60%;
                left: 50%;
                transform: translateX(-50%) rotate(45deg);
            }
            
            .third-base {
                bottom: 40%;
                left: 30%;
            }
            
            .pitchers-mound {
                width: 15px;
                height: 15px;
                background: #c2996c;
                border: 1px solid #866a4b;
                border-radius: 50%;
                position: absolute;
                top: 60%;
                left: 50%;
                transform: translateX(-50%);
            }
            
            .bench {
                margin-top: 20px;
                font-style: italic;
                background: #eee;
                padding: 10px;
                border-radius: 6px;
                text-align: center;
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
            <li>RC/RV - Right Center/Rover</li>
        </ul>
        <p>Positions highlighted in red in the table indicate the player is benched for that inning.</p>
        <p>Positions highlighted in yellow on the field indicate they are occupied by a player in that inning.</p>
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

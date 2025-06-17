import pulp
from models.player import Player
from results_printer import ResultsPrinter
import csv
import os
import json
from datetime import datetime


INPUT_FILE = "./inputs/06-09-2025-roster.csv"
ATTENDANCE_KEY = "06/09"
MIN_NUMBER_GIRLS = 4
FIELDING_POSITION_NAMES = {
    1: "P",  # Pitcher
    2: "C",  # Catcher
    3: "1B",  # First Base
    4: "2B",  # Second Base
    5: "3B",  # Third Base
    6: "SS",  # Shortstop
    7: "LF",  # Left Field
    8: "CF",  # Center Field
    9: "RF",  # Right Field
    10: "RV",  # Rover
}


def yes_no_to_int(value: str) -> int:
    return 1 if value.lower() == "yes" else 0


def parse_position_possibilities(row: dict) -> dict:
    """Parse position possibilities from CSV row position columns."""
    position_columns = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "RV"]
    return {str(i+1): yes_no_to_int(row[pos]) for i, pos in enumerate(position_columns)}


def parse_player_from_row(row: dict) -> Player:
    """Create a Player object from a CSV row."""
    attendance = {
        "04/21": yes_no_to_int(row["Attendance 04/21?"]),
        "04/28": yes_no_to_int(row["Attendance 04/28?"]),
        "05/05": yes_no_to_int(row["Attendance 05/05?"]),
        "05/12": yes_no_to_int(row["Attendance 05/12?"]),
        "05/19": yes_no_to_int(row["Attendance 05/19?"]),
        "06/09": yes_no_to_int(row["Attendance 06/09?"])
    }
    return Player(
        name=row["Name"],
        email=row["Email"],
        is_girl=yes_no_to_int(row["Is Girl?"]),
        batting_skill=int(row["Batting Skill"]),
        attendance=attendance,
        possibilities=parse_position_possibilities(row),
    )


def normalize_batting_skills(players: list[Player]) -> None:
    """Reverse and scale batting skill levels for optimization (lower CSV values = better)."""
    for player in players:
        player.batting_skill = 100 * (1 + (len(players) - player.batting_skill))


def filter_players_by_attendance(players: list[Player], attendance_key: str) -> list[Player]:
    """Filter players based on their attendance for a specific game."""
    return [player for player in players if player.attendance.get(attendance_key, 0)]


def read_in_roster() -> list[Player]:
    roster_file = os.path.join(os.path.dirname(__file__), INPUT_FILE)
    players = []

    with open(roster_file, mode="r") as file:
        reader = csv.DictReader(file)
        players = [parse_player_from_row(row) for row in reader]

    normalize_batting_skills(players)
    return players


def create_multiple_fielding_positions(players, num_configurations=9):
    all_configurations = []
    used_players = set()
    player_uses = {player.name: 0 for player in players}

    for config_index in range(num_configurations):
        filtered_players = filter_players_by_attendance(players, ATTENDANCE_KEY)
        num_players = len(filtered_players)

        # Define fielding positions (10 positions)
        positions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Create a MILP problem for maximizing some objective
        fielding_problem = pulp.LpProblem(
            f"Fielding_Position_Optimization_{config_index}", pulp.LpMaximize
        )

        # Decision variables: x[i][j] is 1 if player i is assigned to position j, 0 otherwise
        x = pulp.LpVariable.dicts(
            f"x_{config_index}", (range(num_players), positions), cat="Binary"
        )

        # Extract skill levels and preferred positions
        skill_levels = [player.batting_skill for player in filtered_players]

        # first_preferred_positions = [player.preferred_position_1 for player in filtered_players]
        # second_preferred_positions = [player.preferred_position_2 for player in filtered_players]
        # third_preferred_positions = [player.preferred_position_3 for player in filtered_players]

        # Objective: Maximize skill level, match preferred positions, and reward unused players
        fielding_problem += pulp.lpSum(
            # assume batting skill also translates to fielding skill
            skill_levels[i] * x[i][j] +
            # Add preference weights for preferred positions
            # (10 if first_preferred_positions[i] == j else 0) * x[i][j] +
            # (5 if second_preferred_positions[i] == j else 0) * x[i][j] +
            # (2 if third_preferred_positions[i] == j else 0) * x[i][j] +
            # get players on field that haven't been used much
            2000
            * (num_configurations - player_uses[filtered_players[i].name])
            * x[i][j]
            +
            # encourage players who were not used in the last inning
            (1000 if filtered_players[i].name not in used_players else 0) * x[i][j] +
            # reward players who are in the same position from a previous inning
            (
                5
                if any(
                    config.get(j) == filtered_players[i]
                    for config in all_configurations
                )
                else 0
            )
            * x[i][j]
            for i in range(num_players)
            for j in positions
        )

        # Constraint: Each player can be assigned to at most one position
        for i in range(num_players):
            fielding_problem += pulp.lpSum(x[i][j] for j in positions) <= 1

        # Constraint: Each position must be filled by exactly one player
        for j in positions:
            fielding_problem += pulp.lpSum(x[i][j] for i in range(num_players)) == 1

        # ensure minimum number of girls are on the field
        genders = [player.is_girl for player in filtered_players]
        fielding_problem += (
            pulp.lpSum(
                genders[i] * x[i][j] for i in range(num_players) for j in positions
            )
            >= MIN_NUMBER_GIRLS
        )

        # Constraint: A player can only be assigned to their preferred positions
        for i in range(num_players):
            for j in positions:
                if str(j) not in filtered_players[i].possibilities:
                    continue
                if filtered_players[i].possibilities[str(j)] == 0:
                    fielding_problem += x[i][j] == 0

        # Solve the problem
        status = fielding_problem.solve()

        # Print results
        ResultsPrinter.print_optimization_status(pulp.LpStatus[status], config_index + 1)
        used_players = set()
        fielding_assignment = {}
        for i in range(num_players):
            for j in positions:
                if pulp.value(x[i][j]) == 1:
                    fielding_assignment[j] = filtered_players[i]
                    used_players.add(filtered_players[i].name)
                    player_uses[filtered_players[i].name] += 1

        all_configurations.append(fielding_assignment)

        ResultsPrinter.print_fielding_results(
            config_index + 1, fielding_assignment, pulp.value(fielding_problem.objective), FIELDING_POSITION_NAMES
        )

    return all_configurations


def create_batting_order(players) -> list[Player]:
    filtered_players = filter_players_by_attendance(players, ATTENDANCE_KEY)
    num_batters = len(filtered_players)

    # Create a MILP problem for maximizing some objective (e.g., total skill level)
    batting_problem = pulp.LpProblem("Batting_Order_Optimization", pulp.LpMaximize)

    # Decision variables: x[i][j] is 1 if person i is in position j, 0 otherwise
    x = pulp.LpVariable.dicts(
        "x", (range(num_batters), range(num_batters)), cat="Binary"
    )

    # Extract skill levels from the players list
    # note: had to reverse order of skill levels, 1 is best in CSV
    skill_levels = [player.batting_skill for player in filtered_players]

    # Weighting factor to prioritize higher positions
    position_weights = [
        num_batters - j for j in range(num_batters)
    ]  # Higher weight for earlier positions

    # Objective: Maximize the weighted total skill level of the batting order
    batting_problem += pulp.lpSum(
        skill_levels[i] * position_weights[j] * x[i][j]
        for i in range(num_batters)
        for j in range(num_batters)
    )

    # Constraint: Each person can be in exactly one position
    for i in range(num_batters):
        batting_problem += pulp.lpSum(x[i][j] for j in range(num_batters)) == 1

    # Constraint: Each position must have exactly one person
    for j in range(num_batters):
        batting_problem += pulp.lpSum(x[i][j] for i in range(num_batters)) == 1

    # Gender information (0 for male, 1 for female) pulled from filtered players
    genders = [player.is_girl for player in filtered_players]

    # TODO fix
    # ratio of girls to guys must always be 6:4 or 3:2 in order and field
    # Constraint: At least two girls in every group of five consecutive batters
    # TODO this constraint can lead to 'infeasible' solutions if there are not enough
    # TODO got around this by allowing any ratio in the last group of 5
    for j in range(0, num_batters - 5, 5):
        batting_problem += (
            pulp.lpSum(
                genders[i] * x[i][j + k]
                for i in range(num_batters)
                for k in range(min(5, num_batters - j))
            )
            >= 2
        )

    # TODO if short on girls, allow for girls to be in order twice and maintain 3:2 ratio

    # Solve the problem
    status = batting_problem.solve()

    # Print results
    # TODO throw exceptin if this status is bad (lookup possible status codes)
    ResultsPrinter.print_optimization_status(pulp.LpStatus[status])
    order = [None] * num_batters
    for i in range(num_batters):
        for j in range(num_batters):
            if pulp.value(x[i][j]) == 1:
                order[j] = i

    batting_order_players = [filtered_players[i] for i in order]
    ResultsPrinter.print_batting_results(batting_order_players, pulp.value(batting_problem.objective))

    return batting_order_players


def main():
    ResultsPrinter.print_main_header()
    players = read_in_roster()
    ResultsPrinter.print_player_roster(players)

    ResultsPrinter.print_batting_order_header()
    batting_order = create_batting_order(players)

    ResultsPrinter.print_fielding_header()
    fielding_configurations = create_multiple_fielding_positions(players)

    # Create a table-like data structure
    table = []
    for position, player in enumerate(batting_order):
        row = [position + 1, player.name]  # Batting order position and player name
        for inning in range(len(fielding_configurations)):
            # Find the player's position for each inning
            player_position = next(
                (
                    pos
                    for pos, p in fielding_configurations[inning].items()
                    if p.name == player.name
                ),
                None,
            )
            row.append(FIELDING_POSITION_NAMES.get(player_position, "Bench"))
        table.append(row)

    # Sort the table by batting order position
    table.sort(key=lambda x: x[0])

    # Generate the filename with the current date
    current_date = datetime.now().strftime("%d_%m_%Y")
    output_file = f"./outputs/rizzler_roster_{current_date}.csv"

    # Write the table to a CSV file
    with open(output_file, mode="w+", newline="") as file:
        writer = csv.writer(file)
        # Write the header
        header = ["Batting Order", "Player Name"] + [
            f"Inning {i + 1}" for i in range(len(fielding_configurations))
        ]
        writer.writerow(header)
        # Write the rows
        writer.writerows(table)

    print(f"Roster saved to {output_file}")


if __name__ == "__main__":
    main()

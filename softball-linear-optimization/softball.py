import pulp
from dataclasses import dataclass, field
from typing import Optional
import csv
import os
import json
from datetime import datetime

FIELDING_POSITION_NAMES = {
    1: "P",   # Pitcher
    2: "C",   # Catcher
    3: "1B",  # First Base
    4: "2B",  # Second Base
    5: "3B",  # Third Base
    6: "SS",  # Shortstop
    7: "LF",  # Left Field
    8: "CF",  # Center Field
    9: "RF",  # Right Field
    10: "RV"  # Rover
}

INFIELDING_POSITIONS = set([
    1, # "P",   # Pitcher
    3, # "1B",  # First Base
    4, # "2B",  # Second Base
    5, # "3B",  # Third Base
    6, # "SS",  # Shortstop
])

@dataclass
class Player:
    name: str
    email: str
    is_girl: int
    batting_skill: int
    attendance_0421: int
    will_infield: int
    preferred_position_1: Optional[int] # e.g., 6 = shortstop
    preferred_position_2: Optional[int] # e.g., 6 = shortstop
    preferred_position_3: Optional[int] # e.g., 6 = shortstop
    # these two fields are just "not is_girl"
    can_1b: int
    can_3b: int


def yes_no_to_int(value: str) -> int:
    return 1 if value.lower() == 'yes' else 0

def parse_preferred_position(value) -> Optional[int]:
    return int(value) if value != 'None' else None

def read_in_roster() -> list[Player]:
    roster_file = os.path.join(os.path.dirname(__file__), "./inputs/04-21-2025-roster.csv")
    players = []

    with open(roster_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            player = Player(
                name=row['Name'],
                email=row['Email'],
                is_girl=yes_no_to_int(row['Is Girl?']),
                batting_skill=int(row['Batting Skill']),
                attendance_0421=yes_no_to_int(row['Attendance 04/21?']),
                will_infield=yes_no_to_int(row['Will Infield?']),
                preferred_position_1=parse_preferred_position(row['Preferred Position 1']),
                preferred_position_2=parse_preferred_position(row['Preferred Position 2']),
                preferred_position_3=parse_preferred_position(row['Preferred Position 3']),
                can_1b=1 if not yes_no_to_int(row['Is Girl?']) else 0,
                can_3b=1 if not yes_no_to_int(row['Is Girl?']) else 0,
            )
            players.append(player)

    
        for player in players:
            player.batting_skill = 100 * (len(players) - player.batting_skill)  # Reverse the skill level for optimization

    return players


def create_multiple_fielding_positions(players, num_configurations=9):
    all_configurations = []
    used_players = set()
    player_uses = {player.name: 0 for player in players}

    for config_index in range(num_configurations):
        # Filter players who have true "attendance_0421" field
        filtered_players = [player for player in players if player.attendance_0421]
        num_players = len(filtered_players)

        # Define fielding positions (10 positions)
        positions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Create a MILP problem for maximizing some objective
        fielding_problem = pulp.LpProblem(f"Fielding_Position_Optimization_{config_index}", pulp.LpMaximize)

        # Decision variables: x[i][j] is 1 if player i is assigned to position j, 0 otherwise
        x = pulp.LpVariable.dicts(f"x_{config_index}", (range(num_players), positions), cat='Binary')

        # Extract skill levels and preferred positions
        skill_levels = [player.batting_skill for player in filtered_players]
        first_preferred_positions = [player.preferred_position_1 for player in filtered_players]
        second_preferred_positions = [player.preferred_position_2 for player in filtered_players]
        third_preferred_positions = [player.preferred_position_3 for player in filtered_players]


        # Objective: Maximize skill level, match preferred positions, and reward unused players
        fielding_problem += pulp.lpSum(
            skill_levels[i] * x[i][j] +
            (10 if first_preferred_positions[i] == j else 0) * x[i][j] +
            (5 if second_preferred_positions[i] == j else 0) * x[i][j] +
            (2 if third_preferred_positions[i] == j else 0) * x[i][j] +
            2000 * (num_configurations - player_uses[filtered_players[i].name]) * x[i][j] +
            (1000 if filtered_players[i].name not in used_players else 0) * x[i][j] +
            (5 if any(config.get(j) == filtered_players[i] for config in all_configurations) else 0) * x[i][j]
            for i in range(num_players) for j in positions
        )

        # Constraint: Each player can be assigned to at most one position
        for i in range(num_players):
            fielding_problem += pulp.lpSum(x[i][j] for j in positions) <= 1

        # Constraint: Each position must be filled by exactly one player
        for j in positions:
            fielding_problem += pulp.lpSum(x[i][j] for i in range(num_players)) == 1

        # Gender constraints: Ensure at least 4 females are on the field
        genders = [player.is_girl for player in filtered_players]
        fielding_problem += pulp.lpSum(genders[i] * x[i][j] for i in range(num_players) for j in positions) >= 4

        # Constraint: A player can only be assigned to an infield position if their "will_infield" field is true
        for i in range(num_players):
            for j in INFIELDING_POSITIONS:
                fielding_problem += x[i][j] <= filtered_players[i].will_infield

        # Solve the problem
        status = fielding_problem.solve()

        # Print results
        print(f"Status for configuration {config_index + 1}: {pulp.LpStatus[status]}")
        used_players = set()
        fielding_assignment = {}
        for i in range(num_players):
            for j in positions:
                if pulp.value(x[i][j]) == 1:
                    fielding_assignment[j] = filtered_players[i]
                    used_players.add(filtered_players[i].name)
                    player_uses[filtered_players[i].name] += 1

        all_configurations.append(fielding_assignment)

        print()
        print("*" * 40)
        print(f"Results for Configuration {config_index + 1}")
        print("*" * 40)
        print("Fielding Positions:")
        for position, player in fielding_assignment.items():
            position_name = FIELDING_POSITION_NAMES.get(position, f"Unknown ({position})")
            print(f"Position {position_name}: {player.name} (Gender: {'Girl' if player.is_girl else 'Boy'}) (Skill: {player.batting_skill})")
        print(f"Objective value: {pulp.value(fielding_problem.objective)}")
        print()

    return all_configurations


def create_batting_order(players) -> list[Player]:
    # Filter players who have true "attendance_0421" field
    filtered_players = [player for player in players if player.attendance_0421]
    num_batters = len(filtered_players)

    # Create a MILP problem for maximizing some objective (e.g., total skill level)
    batting_problem = pulp.LpProblem("Batting_Order_Optimization", pulp.LpMaximize)

    # Decision variables: x[i][j] is 1 if person i is in position j, 0 otherwise
    x = pulp.LpVariable.dicts("x", (range(num_batters), range(num_batters)), cat='Binary')

    # Extract skill levels from the players list
    # note: had to reverse order of skill levels, 1 is best in CSV
    skill_levels = [player.batting_skill for player in filtered_players]

    # Weighting factor to prioritize higher positions
    position_weights = [num_batters - j for j in range(num_batters)]  # Higher weight for earlier positions

    # Objective: Maximize the weighted total skill level of the batting order
    batting_problem += pulp.lpSum(skill_levels[i] * position_weights[j] * x[i][j] 
                                  for i in range(num_batters) for j in range(num_batters))

    # Constraint: Each person can be in exactly one position
    for i in range(num_batters):
        batting_problem += pulp.lpSum(x[i][j] for j in range(num_batters)) == 1

    # Constraint: Each position must have exactly one person
    for j in range(num_batters):
        batting_problem += pulp.lpSum(x[i][j] for i in range(num_batters)) == 1

    # Gender information (0 for male, 1 for female) pulled from filtered players
    genders = [player.is_girl for player in filtered_players]

    # ratio of girls to guys must always be 6:4 or 3:2 in order and field
    # Constraint: At least two females in every group of five consecutive batters
    for j in range(0, num_batters, 5):
        batting_problem += pulp.lpSum(genders[i] * x[i][j + k] for i in range(num_batters) for k in range(min(5, num_batters - j))) >= 2

    # TODO if short on girls, allow for girls to be in order twice and maintain 3:2 ratio

    # Solve the problem
    status = batting_problem.solve()

    # Print results
    print(f"Status: {pulp.LpStatus[status]}")
    order = [None] * num_batters
    for i in range(num_batters):
        for j in range(num_batters):
            if pulp.value(x[i][j]) == 1:
                order[j] = i
    
    print()
    print("*" * 40)
    print("Final Results")
    print("*" * 40)
    print("Batting Order:")
    for position, player_index in enumerate(order):
        print(f"{position + 1}: {filtered_players[player_index].name} (Gender: {'Girl' if filtered_players[player_index].is_girl else 'Boy'}) (Skill: {filtered_players[player_index].batting_skill})")
    print(f"Objective value: {pulp.value(batting_problem.objective)}")
    print()

    return [filtered_players[i] for i in order]


def main():
    print("*" * 40)
    print("Softball Batting Order Optimization")
    print("*" * 40)
    print("*" * 40)
    print("Reading in Roster")
    print("*" * 40)
    players = read_in_roster()
    for player in players:
        print(json.dumps(player.__dict__, indent=4))
    print("*" * 40)
    print("Order Optimization")
    print("*" * 40)
    batting_order = create_batting_order(players)
    print("*" * 40)
    print("Field Optimization")
    print("*" * 40)
    fielding_configurations = create_multiple_fielding_positions(players)

    # Create a table-like data structure
    table = []
    for position, player in enumerate(batting_order):
        row = [position + 1, player.name]  # Batting order position and player name
        for inning in range(len(fielding_configurations)):
            # Find the player's position for each inning
            player_position = next(
                (pos for pos, p in fielding_configurations[inning].items() if p.name == player.name),
                None
            )
            row.append(FIELDING_POSITION_NAMES.get(player_position, "Bench"))
        table.append(row)

    # Sort the table by batting order position
    table.sort(key=lambda x: x[0])

    # Generate the filename with the current date
    current_date = datetime.now().strftime("%d_%m_%Y")
    output_file = f"./outputs/rizzler_roster_{current_date}.csv"

    # Write the table to a CSV file
    with open(output_file, mode='w+', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        header = ["Batting Order", "Player Name"] + [f"Inning {i + 1}" for i in range(len(fielding_configurations))]
        writer.writerow(header)
        # Write the rows
        writer.writerows(table)

    print(f"Roster saved to {output_file}")


if __name__ == "__main__":
    main()
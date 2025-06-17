import json


class ResultsPrinter:
    @staticmethod
    def print_section_header(title: str) -> None:
        print("*" * 40)
        print(title)
        print("*" * 40)
    
    @staticmethod
    def print_player_roster(players) -> None:
        ResultsPrinter.print_section_header("Reading in Roster")
        for player in players:
            print(json.dumps(player.__dict__, indent=4))
    
    @staticmethod
    def print_batting_order_header() -> None:
        ResultsPrinter.print_section_header("Order Optimization")
    
    @staticmethod
    def print_fielding_header() -> None:
        ResultsPrinter.print_section_header("Field Optimization")
    
    @staticmethod
    def print_optimization_status(status: str, config_num: int = None) -> None:
        if config_num is not None:
            print(f"Status for configuration {config_num}: {status}")
        else:
            print(f"Status: {status}")
    
    @staticmethod
    def print_batting_results(batting_order, objective_value: float) -> None:
        ResultsPrinter.print_section_header("Final Results")
        print("Batting Order:")
        for position, player in enumerate(batting_order):
            gender = "Girl" if player.is_girl else "Guy"
            print(f"{position + 1}: {player.name} (Gender: {gender}) (Skill: {player.batting_skill})")
        print(f"Objective value: {objective_value}")
        print()
    
    @staticmethod
    def print_fielding_results(config_num: int, fielding_assignment: dict, objective_value: float, position_names: dict) -> None:
        print()
        print("*" * 40)
        print(f"Results for Configuration {config_num}")
        print("*" * 40)
        print("Fielding Positions:")
        for position, player in fielding_assignment.items():
            position_name = position_names.get(position, f"Unknown ({position})")
            gender = "Girl" if player.is_girl else "Guy"
            print(f"Position {position_name}: {player.name} (Gender: {gender}) (Skill: {player.batting_skill})")
        print(f"Objective value: {objective_value}")
        print()
    
    @staticmethod
    def print_main_header() -> None:
        ResultsPrinter.print_section_header("Softball Batting Order Optimization")
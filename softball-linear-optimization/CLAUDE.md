# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based softball roster optimization tool that uses linear programming to generate optimal batting orders and fielding assignments. The system maximizes team performance while adhering to league constraints like minimum female player requirements and position eligibility.

## Core Architecture

- **Main Script**: `softball.py` - Contains the complete optimization pipeline
- **Data Models**: `models/player.py` - Defines the Player dataclass
- **Input Data**: `inputs/` directory contains CSV roster files for different game dates
- **Output**: `outputs/` directory stores generated roster assignments

## Key Components

### Optimization Engine
The system uses PuLP (Python linear programming library) to solve two optimization problems:
1. **Batting Order**: Maximizes skill-weighted batting positions with gender distribution constraints
2. **Fielding Assignments**: Creates multiple inning configurations balancing player usage, skill levels, and position preferences

### Data Structure
- Players have batting skills (1-best to N-worst in CSV, internally reversed for optimization)
- Position possibilities (1-10) corresponding to P, C, 1B, 2B, 3B, SS, LF, CF, RF, RV
- Attendance tracking for multiple game dates
- Gender information for league compliance

### Configuration Management
- `INPUT_FILE` and `ATTENDANCE_KEY` variables at the top of `softball.py` control which roster and attendance data to use
- `MIN_NUMBER_GIRLS` enforces league gender requirements
- Position mappings defined in `FIELDING_POSITION_NAMES` dictionary

## Running the Tool

```bash
python3 softball.py
```

This will:
1. Read the roster from the configured input file
2. Generate optimal batting order
3. Create 9 inning fielding configurations  
4. Output results to console and save CSV to `outputs/`

## Dependencies

- Python 3.10+
- PuLP 3.0+ (Linear programming solver)
- Standard library: csv, os, json, datetime, dataclasses

## Input File Format

CSV files in `inputs/` must contain these columns:
- Name, Email, Is Girl?, Batting Skill
- Attendance columns for each game date
- Position possibility columns (1-10) with Yes/No values

## Key Constraints

- Each fielding position must be filled by exactly one player
- Players can only be assigned to positions they're eligible for
- Minimum number of female players on field (configurable)
- Batting order maintains gender ratio requirements (2+ girls per 5 consecutive batters)
- Player usage balancing across multiple innings

## Modifying for New Games

1. Add new roster CSV to `inputs/` directory
2. Update `INPUT_FILE` variable in `softball.py`
3. Add corresponding attendance field to Player dataclass
4. Update `ATTENDANCE_KEY` variable to match new field name
# This file contains constraint settings for the Wumpus World game.
# It defines various constants that control the game's behavior, such as grid size, pit probability, and scoring system.
# Wumpus World Configuration Settings

# Game Settings
DEFAULT_GRID_SIZE = 4
DEFAULT_PIT_PROBABILITY = 0.2
DEFAULT_WUMPUS_COUNT = 1
MAX_STEPS = 1000

# Scoring System
GOLD_REWARD = 1000
DEATH_PENALTY = -1000
ARROW_COST = -10
MOVE_COST = -1

# Directions
DIRECTIONS = ['N', 'E', 'S', 'W']
DIRECTION_VECTORS = {
    'N': (0, 1),
    'E': (1, 0), 
    'S': (0, -1),
    'W': (-1, 0)
}

# Agent Types
AGENT_TYPES = {
    'RANDOM': 'random',
    'HYBRID': 'hybrid'
}

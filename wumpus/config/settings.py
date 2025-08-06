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
    (0, 1) : 'N',
    (1, 0) : 'E',
    (0, -1): 'S',
    (-1, 0): 'W'
}

# Agent Types
AGENT_TYPES = {
    'RANDOM': 'random',
    'HYBRID': 'hybrid'
}

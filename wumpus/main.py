from .core.environment import Environment
from .agents.random_agent import RandomAgent
import sys

def run_console():
    env = Environment(N=4)
    agent = RandomAgent(env)

    steps = 0
    while agent.step():
        steps += 1
        if steps > 100:
            print("Agent took too long!")
            break

    print(f"Final Score: {agent.score}")

def run_gui():
    from .GUI.game_board_clean import GameBoardUI
    app = GameBoardUI(seed=11) 
    app.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        run_gui()
    else:
        run_console()



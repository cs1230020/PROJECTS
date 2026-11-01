# AI Game Bot: Rivers and Stones

A game-playing AI agent for **Rivers and Stones**, a two-player board game in which players race to land their stones in the opponent's scoring zone. Built in Python as a course project under Prof. Mausam at IIT Delhi.

## The Game

- Two players, **circle** and **square**, play on boards 12, 14 or 16 columns wide.
- Each piece is either a **stone** or a **river**. Rivers are horizontal or vertical, and any piece that enters a river is carried along its direction, possibly through a chain of connected rivers.
- On each turn a player can **move** a piece, **push** an adjacent piece, **flip** a piece between stone and river, or **rotate** a river.
- A player wins by getting the required number of stones (4, 5 or 6, depending on board width) into their scoring row.

## How the Agent Works

### Move generation
Generates every legal move for the current player, including multi-hop river flows traced with BFS. Pieces already in the scoring zone are restricted to moves that keep them there.

### Search
Uses minimax with alpha–beta pruning (search depth is configurable through `self.depth`). At the root, candidate moves are scored and sorted, and the top alternatives are kept for loop-breaking.

### Evaluation function
Scores a position from the agent's point of view using:

| Component | Weight |
|---|---|
| Stones in scoring zone (ours minus theirs) | 800,000 each |
| Rivers in scoring zone (ours minus theirs) | 500,000 each |
| Advancement score | 2,000 × score |

The **advancement score** runs a BFS shortest-path search for each piece to the goal row, following the game's river-flow movement rules. Pieces are ranked by distance, and the closest ones count most (weights 40, 20, 10, 5, …), each contributing `weight / (distance + 1)`.

### Defensive play
- **Threat detection:** classifies every opponent piece as a critical, high or medium threat based on its BFS distance to the agent's scoring zone.
- **Blocking moves:** evaluates moves that push threatening pieces further away and plays the strongest block when a critical threat is found.
- **Defender pieces:** keeps pieces stationed around its own zone until it has scored two stones.

### Opening and loop avoidance
- Plays a fixed two-move opening suited to each board size.
- Hashes every position it reaches and keeps a short history. If a move would repeat a recent position, it switches to the next-best alternative to escape repetition loops.

## Usage

The agent plugs into the course's game engine (not included in this repo) through the `StudentAgent` class:

```python
from student_agent import StudentAgent

agent = StudentAgent("circle")   # or "square"
move = agent.choose(board, rows, cols, score_cols, time_left, opp_time)
```

`choose()` returns a move dictionary such as:

```python
{"action": "move", "from": [x, y], "to": [x2, y2]}
{"action": "push", "from": [x, y], "to": [x2, y2], "pushed_to": [x3, y3]}
{"action": "flip", "from": [x, y], "orientation": "vertical"}
{"action": "rotate", "from": [x, y]}
```

## Tech Stack

Python · Minimax · Alpha–Beta Pruning · BFS

## Author

**Shashank Kumar**, B.Tech Computer Science and Engineering, IIT Delhi

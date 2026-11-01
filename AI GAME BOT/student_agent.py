"""
Strategic Agent for Rivers and Stones Game
Fresh implementation incorporating advanced tactical analysis
"""

from collections import deque
from typing import List, Dict, Any, Optional, Tuple, Set
from abc import ABC, abstractmethod
import random
import copy

# ==================== CORE GAME PIECES ====================

class Token:
    """Represents a game token with owner and type information."""
    def __init__(self, player: str, face: str = "stone", align: Optional[str] = None):
        self.owner = player
        self.side = face
        self.orientation = align if align else "horizontal"
    
    def duplicate(self):
        return Token(self.owner, self.side, self.orientation)


# ==================== BOARD UTILITIES ====================

def is_valid_position(x: int, y: int, grid_h: int, grid_w: int) -> bool:
    inside_width = 0 <= x < grid_w
    inside_height = 0 <= y < grid_h
    return inside_width and inside_height


def get_score_columns(board_width: int) -> List[int]:
    zone_width = {12: 4, 14: 5, 16: 6}.get(board_width, 4)
    left = (board_width - zone_width) // 2
    start_col = left if left > 0 else 0
    end_col = start_col + zone_width
    return list(range(start_col, end_col))


def circle_scoring_row() -> int:
    return 2


def square_scoring_row(board_height: int) -> int:
    return board_height - 3


def is_enemy_zone(x: int, y: int, player: str, h: int, w: int, cols: List[int]) -> bool:
    if player == "circle":
        target_row = square_scoring_row(h)
    else:
        target_row = circle_scoring_row()

    in_row = y == target_row
    in_col = x in cols
    return in_row and in_col


def is_friendly_zone(x: int, y: int, player: str, h: int, w: int, cols: List[int]) -> bool:
    if player == "circle":
        target_row = circle_scoring_row()
    else:
        target_row = square_scoring_row(h)

    in_correct_row = y == target_row
    in_correct_col = x in cols
    return in_correct_row and in_correct_col


def flip_player(current: str) -> str:
    return "square" if current == "circle" else "circle"


# ==================== RIVER FLOW MECHANICS ====================

def trace_river_flow(board: List[List[Optional[Token]]], 
                     rx: int, ry: int, sx: int, sy: int,
                     player: str, h: int, w: int, 
                     score_cols: List[int]) -> List[Tuple[int, int]]:
    destinations = []
    visited = set()
    queue = deque([(rx, ry)])
    
    while queue:
        cx, cy = queue.popleft()
        
        if (cx, cy) in visited or not is_valid_position(cx, cy, h, w):
            continue
            
        visited.add((cx, cy))

        cell = board[cy][cx]
        
        if cell is None:
            if not is_enemy_zone(cx, cy, player, h, w, score_cols):
                destinations.append((cy, cx))
            continue

        if cell.side != "river":
            continue

        if cell.orientation == "horizontal":
            flow_dirs = [(1, 0), (-1, 0)]
        else:
            flow_dirs = [(0, 1), (0, -1)]

        for dx, dy in flow_dirs:
            nx, ny = cx + dx, cy + dy

            while is_valid_position(nx, ny, h, w):
                if is_enemy_zone(nx, ny, player, h, w, score_cols):
                    break

                next_cell = board[ny][nx]

                if next_cell is None:
                    destinations.append((ny, nx))
                    nx += dx
                    ny += dy
                    continue

                if nx == sx and ny == sy:
                    nx += dx
                    ny += dy
                    continue

                if next_cell.side == "river":
                    queue.append((nx, ny))
                    break

                break
    
    unique = []
    seen = set()
    for dest in destinations:
        if dest not in seen:
            seen.add(dest)
            unique.append(dest)
    
    return unique


# ==================== MOVE GENERATION ====================

def generate_piece_moves(board: List[List[Optional[Token]]], 
                        x: int, y: int, player: str,
                        h: int, w: int, score_cols: List[int]) -> List[Dict[str, Any]]:
    moves = []
    token = board[y][x]
    
    if not token or token.owner != player:
        return moves
    
    cardinal = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    if token.side == "stone":
        for dx, dy in cardinal:
            tx, ty = x + dx, y + dy

            if not is_valid_position(tx, ty, h, w):
                continue
            if is_enemy_zone(tx, ty, player, h, w, score_cols):
                continue

            target = board[ty][tx]

            if target is None:
                moves.append({"action": "move", "from": [x, y], "to": [tx, ty]})
                continue

            if target.side == "river":
                flow_dests = trace_river_flow(
                    board, tx, ty, x, y, player, h, w, score_cols
                )
                for fy, fx in flow_dests:
                    moves.append({"action": "move", "from": [x, y], "to": [fx, fy]})
                continue

            if target.side == "stone":
                px, py = tx + dx, ty + dy
                if (
                    is_valid_position(px, py, h, w)
                    and board[py][px] is None
                    and not is_enemy_zone(px, py, target.owner, h, w, score_cols)
                ):
                    moves.append(
                        {
                            "action": "push",
                            "from": [x, y],
                            "to": [tx, ty],
                            "pushed_to": [px, py],
                        }
                    )
        
        moves.append({"action": "flip", "from": [x, y], "orientation": "horizontal"})
        moves.append({"action": "flip", "from": [x, y], "orientation": "vertical"})
    
    else:
        for dx, dy in cardinal:
            tx, ty = x + dx, y + dy
            
            if not is_valid_position(tx, ty, h, w):
                continue
            if is_enemy_zone(tx, ty, player, h, w, score_cols):
                continue
            
            target = board[ty][tx]
            
            if target is None:
                moves.append({"action": "move", "from": [x, y], "to": [tx, ty]})
            elif target.side == "river":
                flow_dests = trace_river_flow(board, tx, ty, x, y, player, h, w, score_cols)
                for fy, fx in flow_dests:
                    moves.append({"action": "move", "from": [x, y], "to": [fx, fy]})
            elif target.side == "stone":
                flow_dests = trace_river_flow(board, tx, ty, x, y, target.owner, h, w, score_cols)
                for fy, fx in flow_dests:
                    if not is_enemy_zone(fx, fy, player, h, w, score_cols):
                        moves.append({"action": "push", "from": [x, y], "to": [tx, ty], "pushed_to": [fx, fy]})
        
        moves.append({"action": "flip", "from": [x, y]})
        moves.append({"action": "rotate", "from": [x, y]})
    
    return moves


def compile_all_moves(board: List[List[Any]], player: str, 
                     h: int, w: int, score_cols: List[int],
                     include_defenders: bool = False) -> List[Dict[str, Any]]:
    
    if player == "circle":
        defense_row = square_scoring_row(h)
        defenders = set()
        for col in score_cols:
            defenders.add((defense_row - 1, col))
        defenders.add((defense_row, score_cols[0] - 1))
        defenders.add((defense_row, score_cols[-1] + 1))
    else:
        defense_row = circle_scoring_row()
        defenders = set()
        for col in score_cols:
            defenders.add((defense_row + 1, col))
        defenders.add((defense_row, score_cols[0] - 1))
        defenders.add((defense_row, score_cols[-1] + 1))
    
    scoring_count = sum(1 for y in range(h) for x in range(w)
                       if board[y][x] and board[y][x].owner == player and 
                       board[y][x].side == "stone" and 
                       is_friendly_zone(x, y, player, h, w, score_cols))
    
    if not include_defenders and scoring_count >= 2:
        defenders = set()
    
    all_moves = []

    for y in range(h):
        for x in range(w):
            token = board[y][x]

            if not token or token.owner != player:
                continue

            if not include_defenders and (y, x) in defenders:
                continue

            piece_moves = generate_piece_moves(board, x, y, player, h, w, score_cols)
            
            if is_friendly_zone(x, y, player, h, w, score_cols):
                filtered = []
                for move in piece_moves:
                    if move["action"] == "move":
                        dest_x, dest_y = move["to"]
                        if is_friendly_zone(dest_x, dest_y, player, h, w, score_cols):
                            filtered.append(move)
                    elif move["action"] == "push":
                        dest_x, dest_y = move["to"]
                        push_x, push_y = move["pushed_to"]
                        
                        target = board[dest_y][dest_x]
                        if (target and target.owner == player and
                            is_friendly_zone(dest_x, dest_y, player, h, w, score_cols) and
                            not is_friendly_zone(push_x, push_y, player, h, w, score_cols)):
                            continue
                        
                        if is_friendly_zone(dest_x, dest_y, player, h, w, score_cols):
                            filtered.append(move)
                    elif move["action"] in ["flip", "rotate"]:
                        filtered.append(move)
                
                all_moves.extend(filtered)
            else:
                all_moves.extend(piece_moves)
    
    return all_moves


# ==================== PATHFINDING WITH BFS ====================

def compute_path_distance(board: List[List[Token]], start_x: int, start_y: int,
                         h: int, w: int, goal_zone: Set[Tuple[int, int]],
                         pathfinder_player: str) -> float:
    score_cols = get_score_columns(w)
    
    if (start_y, start_x) in goal_zone:
        return 0.0
    
    queue = deque([(start_y, start_x, 0.0)])
    visited = {(start_y, start_x): 0.0}
    
    while queue:
        cy, cx, cost = queue.popleft()
        
        if (cy, cx) in goal_zone and not board[cy][cx]:
            bonus = 0.0
            for offset in range(1, len(score_cols)):
                if cx + offset <= score_cols[-1] and not board[cy][cx + offset]:
                    bonus += 0.001
                if cx - offset >= score_cols[0] and not board[cy][cx - offset]:
                    bonus += 0.001
            return cost - bonus
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            
            if not is_valid_position(nx, ny, h, w):
                continue
            if (ny, nx) in visited:
                continue
            
            neighbor = board[ny][nx]
            
            if neighbor is None:
                visited[(ny, nx)] = cost + 1
                queue.append((ny, nx, cost + 1))
            elif neighbor.side == "river":
                flow_exits = trace_river_flow(board, nx, ny, cx, cy, pathfinder_player, h, w, score_cols)
                for exit_y, exit_x in flow_exits:
                    if (exit_y, exit_x) not in visited:
                        visited[(exit_y, exit_x)] = cost + 1
                        queue.append((exit_y, exit_x, cost + 1))
    
    return float('inf')


# ==================== STRATEGIC EVALUATION ====================

def count_stones_in_zone(board: List[List[Optional[Token]]],
                        player: str, h: int, w: int, cols: List[int]) -> int:
    count = 0
    for y, row in enumerate(board):
        for x, token in enumerate(row):
            if (token and token.owner == player and token.side == "stone" and
                is_friendly_zone(x, y, player, h, w, cols)):
                count += 1
    return count


def count_rivers_in_zone(board: List[List[Optional[Token]]],
                         player: str, h: int, w: int, cols: List[int]) -> int:
    count = 0
    for y, row in enumerate(board):
        for x, token in enumerate(row):
            if (token and token.owner == player and token.side == "river" and
                is_friendly_zone(x, y, player, h, w, cols)):
                count += 1
    return count


def calculate_advancement_score(board: List[List[Token]], player: str,
                                h: int, w: int, score_cols: List[int]) -> float:
    if player == "circle":
        goal_row = circle_scoring_row()
        defend_row = square_scoring_row(h)
    else:
        goal_row = square_scoring_row(h)
        defend_row = circle_scoring_row()
    
    defenders = set()
    for col in score_cols:
        if player == "circle":
            defenders.add((defend_row - 1, col))
        else:
            defenders.add((defend_row + 1, col))
    
    if player == "circle":
        defenders.add((defend_row, score_cols[0] - 1))
        defenders.add((defend_row, score_cols[-1] + 1))
    else:
        defenders.add((defend_row, score_cols[0] - 1))
        defenders.add((defend_row, score_cols[-1] + 1))
    
    if count_stones_in_zone(board, player, h, w, score_cols) >= 2:
        defenders = set()
    
    goal_cells = {(goal_row, col) for col in score_cols}
    
    piece_distances = []
    
    for y in range(h):
        for x in range(w):
            token = board[y][x]
            if (token and token.owner == player and 
                (y, x) not in defenders and (y, x) not in goal_cells):
                
                distance = compute_path_distance(board, x, y, h, w, goal_cells, player)
                
                if token.side == "river":
                    distance += 0.0001
                
                piece_distances.append((distance, x, y))
    
    if not piece_distances:
        return 0.0
    
    piece_distances.sort()
    
    importance_weights = [40.0, 20.0, 10.0, 5.0, 2.5, 1.25]
    
    stones_scored = count_stones_in_zone(board, player, h, w, score_cols)
    rivers_scored = count_rivers_in_zone(board, player, h, w, score_cols)
    total_scored = stones_scored + rivers_scored
    
    target_count = {12: 4, 14: 5, 16: 6}.get(w, 4)
    pieces_needed = target_count - total_scored
    
    advancement_value = 0.0
    
    for idx in range(min(pieces_needed, len(piece_distances))):
        dist, _, _ = piece_distances[idx]
        weight = importance_weights[min(idx, 5)]
        
        if dist != float('inf'):
            contribution = (1.0 / (dist + 1.0)) * weight
            advancement_value += contribution
    
    return advancement_value if advancement_value > 0 else -1.0


def assess_threats(board: List[List[Token]], player: str,
                  h: int, w: int, score_cols: List[int]) -> Tuple[List, List, List]:
    opponent = flip_player(player)
    
    if player == "circle":
        our_score_row = square_scoring_row(h)
    else:
        our_score_row = circle_scoring_row()
    
    our_goal_zone = {(our_score_row, col) for col in score_cols}
    
    critical_threats = []
    high_threats = []
    medium_threats = []
    
    for y in range(h):
        for x in range(w):
            token = board[y][x]
            
            if token and token.owner == opponent and (y, x) not in our_goal_zone:
                distance = compute_path_distance(board, x, y, h, w, our_goal_zone, opponent)
                
                if distance < 1.5:
                    critical_threats.append((y, x, distance))
                elif distance < 2.5:
                    high_threats.append((y, x, distance))
                elif distance < 3.5:
                    medium_threats.append((y, x, distance))
    
    return critical_threats, high_threats, medium_threats


EVAL_CONFIG = {
    'stone_in_goal': 800000,
    'river_in_goal': 500000,
    'advancement': 2000,
}


def evaluate_position(board: List[List[Any]], player: str,
                     h: int, w: int, score_cols: List[int]) -> float:
    opponent = flip_player(player)
    
    score = 0.0
    
    our_stones = count_stones_in_zone(board, player, h, w, score_cols)
    opp_stones = count_stones_in_zone(board, opponent, h, w, score_cols)
    our_rivers = count_rivers_in_zone(board, player, h, w, score_cols)
    opp_rivers = count_rivers_in_zone(board, opponent, h, w, score_cols)
    
    score += (our_stones - opp_stones) * EVAL_CONFIG['stone_in_goal']
    score += (our_rivers - opp_rivers) * EVAL_CONFIG['river_in_goal']
    
    score += calculate_advancement_score(board, player, h, w, score_cols) * EVAL_CONFIG['advancement']
    
    return score


# ==================== MOVE APPLICATION ====================

def apply_move(board: List[List[Any]], move: Dict[str, Any],
              player: str, h: int, w: int, score_cols: List[int]) -> Tuple[bool, Any]:
    board_copy = copy.deepcopy(board)
    
    try:
        action = move["action"]
        from_x, from_y = move["from"]
        token = board_copy[from_y][from_x]
        
        if not token or token.owner != player:
            return False, "Invalid token"
        
        if action == "move":
            to_x, to_y = move["to"]
            if not is_valid_position(to_x, to_y, h, w):
                return False, "Out of bounds"
            if board_copy[to_y][to_x] is not None:
                return False, "Occupied"
            board_copy[to_y][to_x] = token
            board_copy[from_y][from_x] = None
            
        elif action == "push":
            to_x, to_y = move["to"]
            push_x, push_y = move["pushed_to"]
            
            if not is_valid_position(to_x, to_y, h, w):
                return False, "Out of bounds"
            if not is_valid_position(push_x, push_y, h, w):
                return False, "Push out of bounds"
            
            pushed_token = board_copy[to_y][to_x]
            if not pushed_token:
                return False, "Nothing to push"
            if board_copy[push_y][push_x] is not None:
                return False, "Push destination occupied"
            
            board_copy[push_y][push_x] = pushed_token
            board_copy[to_y][to_x] = token
            board_copy[from_y][from_x] = None
            
        elif action == "flip":
            if token.side == "stone":
                orientation = move.get("orientation", "horizontal")
                board_copy[from_y][from_x] = Token(token.owner, "river", orientation)
            else:
                board_copy[from_y][from_x] = Token(token.owner, "stone", None)
                
        elif action == "rotate":
            if token.side != "river":
                return False, "Can only rotate rivers"
            new_orient = "vertical" if token.orientation == "horizontal" else "horizontal"
            board_copy[from_y][from_x] = Token(token.owner, "river", new_orient)
        
        return True, board_copy
        
    except Exception as e:
        return False, str(e)


# ==================== STATE HASHING ====================

def compute_state_hash(board: List[List[Any]], h: int, w: int) -> int:
    hash_val = 0
    for y in range(h):
        for x in range(w):
            token = board[y][x]
            if token:
                pos_component = (y * w + x) * 1000
                owner_component = 1 if token.owner == "circle" else 2
                side_component = 10 if token.side == "stone" else 20
                hash_val ^= (pos_component + owner_component + side_component)
    return hash_val


# ==================== AGENT BASE CLASS ====================

class AgentBase(ABC):
    __slots__ = ("player", "_opponent")

    def __init__(self, player: str):
        self.player = player
        self._opponent = flip_player(player)

    @property
    def opponent(self) -> str:
        return self._opponent

    @abstractmethod
    def choose(
        self,
        board: List[List[Any]],
        rows: int,
        cols: int,
        score_cols: List[int],
        time_left: float,
        opp_time: float,
    ) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


# ==================== STRATEGIC AGENT ====================

move_counter = 0


class StudentAgent(AgentBase):
    
    def __init__(self, player: str):
        super().__init__(player)
        self.depth = 1
        self.position_history = []
        self.history_size = 6
        self.best_alternatives = []
    
    def minimax(self, board: List[List[Any]], depth: int,
               alpha: float, beta: float, maximizing: bool,
               active: str, h: int, w: int, cols: List[int]) -> Tuple[float, Optional[Dict], bool]:
        
        if depth == 0:
            return evaluate_position(board, self.player, h, w, cols), None, True
        
        our_score = count_stones_in_zone(board, self.player, h, w, cols)
        opp_score = count_stones_in_zone(board, self.opponent, h, w, cols)
        win_target = {12: 4, 14: 5, 16: 6}.get(w, 4)
        
        if our_score >= win_target:
            return 10000, None, True
        if opp_score >= win_target:
            return -10000, None, True
        
        moves = compile_all_moves(board, active, h, w, cols, False)
        defense_moves = compile_all_moves(board, active, h, w, cols, True)
        
        if not moves:
            return evaluate_position(board, self.player, h, w, cols), None, True
        
        if depth == self.depth and maximizing:
            scored_moves = []

            for move in moves:
                success, new_board = apply_move(board, move, active, h, w, cols)

                if not success:
                    continue

                eval_val = evaluate_position(new_board, self.player, h, w, cols)
                scored_moves.append((eval_val, move))
            
            scored_moves.sort(key=lambda x: x[0], reverse=True)
            moves = [m for _, m in scored_moves]
            
            if scored_moves:
                best_val = scored_moves[0][0]
                best_move = scored_moves[0][1]
            else:
                best_val = float('-inf')
                best_move = None
            
            self.best_alternatives = scored_moves[:4]
        
        tier1, tier2, tier3 = assess_threats(board, self.player, h, w, cols)
        
        if maximizing:
            best_defense_score = float('-inf')
            best_defense_move = None
            
            for dmove in defense_moves:
                success, projected = apply_move(board, dmove, active, h, w, cols)
                if not success:
                    continue
                
                if self.player == "circle":
                    defend_zone = {(square_scoring_row(h), c) for c in cols}
                else:
                    defend_zone = {(circle_scoring_row(), c) for c in cols}
                
                defense_value = 0
                
                for threat in tier1:
                    ty, tx, _ = threat
                    new_dist = compute_path_distance(projected, tx, ty, h, w, defend_zone, self.opponent)
                    if new_dist >= 1.5 and new_dist < float('inf'):
                        defense_value += 100
                
                for threat in tier2:
                    ty, tx, _ = threat
                    new_dist = compute_path_distance(projected, tx, ty, h, w, defend_zone, self.opponent)
                    if new_dist >= 3.5 and new_dist < float('inf'):
                        if count_stones_in_zone(board, self.opponent, h, w, cols) >= win_target - 1:
                            defense_value += 100
                        else:
                            defense_value += 50
                
                for threat in tier3:
                    ty, tx, _ = threat
                    new_dist = compute_path_distance(projected, tx, ty, h, w, defend_zone, self.opponent)
                    if new_dist >= 5.5 and new_dist < float('inf'):
                        defense_value += 30
                
                if defense_value > best_defense_score:
                    best_defense_score = defense_value
                    best_defense_move = dmove
            
            if best_defense_score >= 100 and best_defense_move is not None:
                return best_val, best_defense_move, False
            
            return best_val, best_move, True
        
        else:
            worst_val = float('inf')
            worst_move = None
            
            for move in moves:
                success, new_board = apply_move(board, move, active, h, w, cols)
                if success:
                    eval_val, _, _ = self.minimax(new_board, depth - 1, alpha, beta,
                                                  True, self.player, h, w, cols)
                    if eval_val < worst_val:
                        worst_val = eval_val
                        worst_move = move
                    
                    beta = min(beta, eval_val)
                    if beta <= alpha:
                        break
            
            return worst_val, worst_move, True
    
    def choose(self, board: List[List[Any]], rows: int, cols: int,
              score_cols: List[int], time_left: float, opp_time: float) -> Optional[Dict[str, Any]]:
        global move_counter
        
        possible = compile_all_moves(board, self.player, rows, cols, score_cols, False)
        
        if not possible:
            return None
        
        if len(possible) == 1:
            return possible[0]
        
        chosen = None
        check_loops = True
        
        if move_counter == 0:
            opening_cols = {12: (3, 8), 14: (3, 9), 16: (4, 11)}.get(cols, (3, 8))
            
            if self.player == "circle":
                chosen = {"action": "move", "from": [opening_cols[0], rows - 4], 
                         "to": [opening_cols[0], rows - 3]}
            else:
                chosen = {"action": "move", "from": [opening_cols[0], 3], 
                         "to": [opening_cols[0], 2]}
            
            move_counter += 1
            check_loops = True
            
        elif move_counter == 1:
            opening_cols = {12: (3, 8), 14: (3, 9), 16: (4, 11)}.get(cols, (3, 8))
            
            if self.player == "circle":
                chosen = {"action": "move", "from": [opening_cols[1], rows - 4], 
                         "to": [opening_cols[1], rows - 3]}
            else:
                chosen = {"action": "move", "from": [opening_cols[1], 3], 
                         "to": [opening_cols[1], 2]}
            
            move_counter += 1
            check_loops = True
            
        else:
            self.best_alternatives = []
            _, chosen, check_loops = self.minimax(board, self.depth, float('-inf'), 
                                                  float('inf'), True, self.player, 
                                                  rows, cols, score_cols)
        
        if chosen and check_loops:
            success, new_board = apply_move(board, chosen, self.player, rows, cols, score_cols)
            
            if success:
                new_hash = compute_state_hash(new_board, rows, cols)
                recent_hashes = [h for h, _ in self.position_history]
                repetitions = recent_hashes.count(new_hash)
                
                if repetitions >= 2:
                    if hasattr(self, 'best_alternatives') and len(self.best_alternatives) > 1:
                        primary_score = self.best_alternatives[0][0]
                        catastrophic_drop = 10000000000
                        
                        for i, (alt_score, alt_move) in enumerate(self.best_alternatives[1:], 1):
                            alt_success, alt_board = apply_move(board, alt_move, self.player, 
                                                               rows, cols, score_cols)
                            if alt_success:
                                alt_hash = compute_state_hash(alt_board, rows, cols)
                                alt_reps = recent_hashes.count(alt_hash)
                                score_diff = primary_score - alt_score
                                
                                if score_diff > catastrophic_drop:
                                    continue
                                
                                if alt_reps < 3:
                                    chosen = alt_move
                                    new_hash = alt_hash
                                    break
                
                self.position_history.append((new_hash, chosen))
                if len(self.position_history) > self.history_size:
                    self.position_history.pop(0)
        
        if chosen and "action" in chosen and "from" in chosen:
            return chosen
        else:
            return random.choice(possible)
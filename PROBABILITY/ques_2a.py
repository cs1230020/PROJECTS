import numpy as np
import random
class Alice:
    def __init__(self):
        self.past_play_styles = np.array([1,1])
        self.results = np.array([1,0])
        self.opp_play_styles = np.array([1,1])
        self.points = 1
        
    def play_move(self):
        if len(self.past_play_styles) == 0:
            return 1

        if len(self.results) > 0:
            previous_result = self.results[-1]
        if previous_result == 0:
            return 1
        elif previous_result == 0.5:
            return 0
        else:
            wins_A = self.points
            losses_B = len(self.results) - wins_A
            prob_A = losses_B / (wins_A + losses_B)
            if prob_A > payoff_matrix[2][0][0]:
                return 0
            else:
                return 2

        return 1
        
    
    def observe_result(self, own_style, opp_style, result):
        
        self.past_play_styles = np.append(self.past_play_styles,own_style)
        self.results = np.append(self.results, result)
        self.opp_play_styles = np.append(self.opp_play_styles,opp_style)
        self.points += result

class Bob:
    def __init__(self):
        self.past_play_styles = np.array([1,1])
        self.results = np.array([1,0])
        self.opp_play_styles = np.array([1,1])
        self.points = 1

    def play_move(self):
        if len(self.results) == 0:
            return 1
        else:
            previous_result = self.results[-1]
            if previous_result == 1:
                return 2
            elif previous_result == 0.5:
                return 1
            else:
                return 0

    def observe_result(self, own_style, opp_style, result):
        self.past_play_styles = np.append(self.past_play_styles, own_style)
        self.results = np.append(self.results, result)
        self.opp_play_styles = np.append(self.opp_play_styles, opp_style)
        self.points += result

alice = Alice()
bob = Bob()
 
payoff_matrix = [
        [[1/2,0,1/2],[7/10,0,3/10],[5/11,0,6/11]],
        [[3/10,0,7/10],[1/3,1/3,1/3],[3/10,1/2,1/5]],
        [[6/11,0,5/11],[1/5,1/2,3/10],[1/10,4/5,1/10]]
]

def simulate_round(player_A, player_B, payoff_matrix):
    move_A = player_A.play_move()
    move_B = player_B.play_move()

    probabilities = payoff_matrix[move_A][move_B]
    
    outcome = random.choices([1, 0.5, 0], weights=probabilities)[0]
    player_A.observe_result(move_A, move_B, outcome)
    player_B.observe_result(move_B, move_A, 1 - outcome)

def monte_carlo(num_rounds):
    for _ in range(num_rounds):
        simulate_round(alice, bob, payoff_matrix)

    print(f"Alice's points: {alice.points}, Bob's points: {bob.points}")


if __name__ == "__main__":
    monte_carlo(num_rounds=10**5)

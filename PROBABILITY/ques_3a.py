import numpy as np
import random
class Alice:
    def __init__(self):
        self.past_play_styles = np.array([1, 1])
        self.results = np.array([1, 0])
        self.opp_play_styles = np.array([1, 1])
        self.points = 1

    def play_move(self):
        payoff_matrix = [
    [[1/2, 0, 1/2], [7/10, 0, 3/10], [5/11, 0, 6/11]],
    [[3/10, 0, 7/10], [1/3, 1/3, 1/3], [3/10, 1/2, 1/5]],
    [[6/11, 0, 5/11], [1/5, 1/2, 3/10], [1/10, 4/5, 1/10]]]
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
                if prob_A <= payoff_matrix[2][0][0]:
                    return 2
                else:
                    return 0
        return 1

    def observe_result(self, own_style, opp_style, result):
    
        self.past_play_styles = np.append(self.past_play_styles, own_style)
        self.results = np.append(self.results, result)
        self.opp_play_styles = np.append(self.opp_play_styles, result)
        self.points += result


class Bob:
    def __init__(self):
        self.past_play_styles = np.array([1, 1])
        self.results = np.array([0, 1])
        self.opp_play_styles = np.array([1, 1])
        self.points = 1

    def play_move(self):
        
        if len(self.results) == 0:
            return 1
        else:
            previous_result = self.results[-1]
            if previous_result == 0.5:
                return 1
            elif previous_result == 1:
                return 2
            else:
                return 0

    def observe_result(self,own_style, opp_style, outcome):
        
        self.points += outcome
        self.past_play_styles = np.append(self.past_play_styles, own_style)
        self.results = np.append(self.results, outcome)
        
        self.opp_play_styles = np.append(self.opp_play_styles, opp_style)
 

payoff_matrix = [
        [[1/2,0,1/2],[7/10,0,3/10],[5/11,0,6/11]],
        [[3/10,0,7/10],[1/3,1/3,1/3],[3/10,1/2,1/5]],
        [[6/11,0,5/11],[1/5,1/2,3/10],[1/10,4/5,1/10]]]

alice = Alice()
bob = Bob()
def simulate_round(alice, bob, payoff_matrix):
    alice_move = alice.play_move()
    bob_move = bob.play_move()
    prob = payoff_matrix[alice_move][bob_move]
    results = random.choices([1,0.5,0], weights = prob)[0]
    alice.observe_result(alice_move,bob_move,results)
    if results!=0.5:
        bob.observe_result(bob_move,alice_move,1-results)
    else:
        bob.observe_result(bob_move,alice_move,results)


def monte_carlo(num_rounds):
    for i in range(num_rounds):
        simulate_round(alice, bob, payoff_matrix)

    print("Alice's points: ", alice.points," Bob's points: ", bob.points)
    
if __name__ == "__main__":
    monte_carlo(num_rounds=10**5)

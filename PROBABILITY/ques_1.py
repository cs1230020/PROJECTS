
M=1000000007

def mod_add(a, b):
    a=(a%M+M)%M
    b=(b%M+M)%M
    return (a+b)%M

def mod_multiply(a, b):
    a=(a%M+M)%M
    b=(b%M+M)%M
    return (a*b)%M

def mod_divide(a, b):
    a=(a%M+M)%M
    b=(b%M+M)%M
    return mod_multiply(a, pow(b, M-2, M))

def calc_prob(alice_wins, bob_wins):
    T=alice_wins+bob_wins
    dp = []
    for i in range(alice_wins + 1):
        row = []
        for j in range(T + 1):
            row.append(0)
        dp.append(row)
    dp[1][2] = 1
    i = 1
    while i <= alice_wins:
        j = 3
        while j <= T:
            if j >= i:
                term1 = mod_divide(i, j - 1)
                term2 = mod_divide(j - i, j - 1)
                left_side = mod_multiply(dp[i][j - 1], term1)
                right_side = mod_multiply(dp[i - 1][j - 1], term2)
                dp[i][j] = mod_add(left_side, right_side)
            j += 1
        i += 1

    result = dp[alice_wins][T]
    return result
    
def calc_expectation(total_games):
    """
    Returns:
        The expected value of sum_{i=1}^{total_games} Xi will be of the form p/q,
        where p and q are positive integers,
        return p.q^(-1) mod 1000000007.
    """
    expectation_value = 0
    current_game = 1
    
    while current_game <= total_games:
        probability = calc_prob(current_game, total_games - current_game)
        term = mod_multiply(2 * current_game - total_games, probability)
        expectation_value = mod_add(expectation_value, term)
        current_game += 1
    
    return expectation_value
alice_wins = 99
bob_wins = 29
T = alice_wins + bob_wins
probability_result = calc_prob(alice_wins, bob_wins)
print(f"Probability Result: {probability_result}")


def calc_variance(total_trials):
    """
    Returns:
        The variance of sum_{i=1}^{total_trials} Xi will be of the form p/q,
        where p and q are positive integers,
        return p.q^(-1) mod 1000000007.
    """
    variance_value = 0
    trial = 1
    
    while trial <= total_trials:
        probability_term = calc_prob(trial, total_trials - trial)
        term = mod_multiply((2 * trial - total_trials) ** 2, probability_term)
        variance_value = mod_add(variance_value, term)
        trial += 1
    
    return variance_value
T = 29
result = calc_expectation(T)
print(result)
T = 29
result1 = calc_variance(T)
print(result1)

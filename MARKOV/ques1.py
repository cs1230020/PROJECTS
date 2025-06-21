



def win_probability(p,q, k, N):
    """
    Returns the probability of winning the game starting with 'k' dollars.
    
    p : float, 0 < p < 1, probability of winning a round
    k : int, starting wealth (0 <= k <= N)
    N : int, maximum wealth (N > k)
    """
    t=q/p
    if p==0.5:
        return k/N
    else:
        return (1-t**k)/(1-t**N)


def limit_win_probability(p,q, k):
    """
    Returns the probability of winning when the maximum wealth is infinity.
    
    p : float, 0 < p < 1, probability of winning a round
    k : int, starting wealth
    """
    t=q/p
    if p <= 0.5:
        return 0 
    else:
        return 1-t**k


def game_duration(p, q, k, N):
    """
    Returns the expected number of rounds until either winning or getting ruined.
    
    p : float, 0 < p < 1, probability of winning a round
    k : int, starting wealth (0 <= k <= N)
    N : int, maximum wealth (N > k)
    """
    # Handle boundary conditions
    if k == 0 or k == N:
        return 0
    
    # Special case for fair game (p = q = 0.5)
    if p == 0.5:
        return k * (N-k)
    
    # For the general case, use the solution to the recurrence relation
    # E_i = 1 + p*E_{i+1} + q*E_{i-1}
    r=q/p
    t=(r+1)/(r-1)
    a=(1-r**k)/(1-r**N)
    return t*(k-N*a)



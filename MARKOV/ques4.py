import numpy as np

def stationary_distribution(p, q, r, N):
    """
    Return a list of size N+1 containing the stationary distribution of the Markov chain.
    
    p : array of size N+1, 0 < p[i] < 1, probability of price increase
    q : array of size N+1, 0 < q[i] < 1, probability of price decrease
    r : array of size N+1, r[i] = 1 - p[i] - q[i], probability of price remaining the same
    N : int, the maximum price of the stock
    """
    # Create transition matrix
    P = np.zeros((N + 1, N + 1))
    
    # Fill in transition probabilities
    for k in range(N + 1):
        if k > 0:
            P[k, k - 1] = q[k]  # probability of decreasing
        P[k, k] = r[k]  # probability of staying the same
        if k < N:
            P[k, k + 1] = p[k]  # probability of increasing
    
    # Solve for the stationary distribution
    A = np.append(P.T - np.eye(N + 1), [np.ones(N + 1)], axis=0)
    b = np.append(np.zeros(N + 1), 1)
    pi = np.linalg.lstsq(A, b, rcond=None)[0]
    
    return pi
def expected_wealth(p, q, r, N):
    """
    Return the expected wealth of the gambler in the long run.

    p : array of size N+1, 0 < p[i] < 1, probability of price increase
    q : array of size N+1, 0 < q[i] < 1, probability of price decrease
    r : array of size N+1, r[i] = 1 - p[i] - q[i], probability of price remaining the same
    N : int, the maximum price of the stock
    """
    t = stationary_distribution(p,q,r,N)   
    exp_wealth = 0
    i=0
    while i<=N:
    
        exp_wealth+=t[i]*i
        i+=1
    return exp_wealth

def expected_time(p, q, r, N, a, b):
    """
    Return the expected time for the price to reach b starting from a.

    p : array of size N+1, 0 < p[i] < 1, probability of price increase
    q : array of size N+1, 0 < q[i] < 1, probability of price decrease
    r : array of size N+1, r[i] = 1 - p[i] - q[i], probability of price remaining the same
    N : int, the maximum price of the stock
    a : int, the starting price
    b : int, the target price
    """
    matrix_A = []
    vector_B = []
    i = 0
    
    while i < b:
        row_temp =[]
        for j in range(b+1):
            row_temp.append(0)
        if i == 0:
            row_temp[i] = 1 - r[i]
            row_temp[i + 1] = -p[i]
            vector_B.append(1)
            matrix_A.append(row_temp)
        else:
            row_temp[i - 1] = -q[i]
            row_temp[i] = 1 - r[i]
            row_temp[i + 1] = -p[i]
            
            vector_B.append(1)
            matrix_A.append(row_temp)
        
        i += 1
    
    last_row = []
    for j in range(b):
        last_row.append(0)
    last_row.append(1)
    matrix_A.append(last_row)
    vector_B.append(0)
    
    vector_B = np.array(vector_B)
    matrix_A = np.array(matrix_A)
    
    
    solution_x = np.linalg.solve(matrix_A, vector_B)
    
    return solution_x[a]





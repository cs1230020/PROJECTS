

def decimalToBinary(num, k_prec):
    """
    Convert a decimal fraction to binary representation up to k_prec bits after the decimal point.
    """
    binary = ""
    Integral = int(num)
    fractional = num - Integral

    # Convert the integer part to binary
    while Integral:
        rem = Integral % 2
        binary += str(rem)
        Integral //= 2

    binary = binary[::-1]
    binary += '.'

    # Convert the fractional part to binary
    while k_prec:
        fractional *= 2
        fract_bit = int(fractional)

        if fract_bit == 1:
            fractional -= fract_bit
            binary += '1'
        else:
            binary += '0'
        k_prec -= 1

    return binary

def is_power_of_2(n):
    """Check if a number is a power of 2."""
    return (n != 0) and (n & (n - 1)) == 0

def recursive_win_probability(curr_wealth, max_wealth, prob_win, prob_loss, cache, max_depth, depth=0):
    """
    Recursive helper to calculate the probability of winning from wealth curr_wealth with depth limit.
    """
    if curr_wealth >= max_wealth:
        return 1.0  # Winning state
    if curr_wealth == 0 or depth >= max_depth:
        return 0.0  # Ruin state or reached maximum recursion depth

    if curr_wealth in cache:
        return cache[curr_wealth]

    if curr_wealth >= max_wealth / 2:
        half_step = 2 * curr_wealth - max_wealth
        if half_step >= 0:
            cache[curr_wealth] = prob_win + prob_loss * recursive_win_probability(
                half_step, max_wealth, prob_win, prob_loss, cache, max_depth, depth + 1
            )
        else:
            cache[curr_wealth] = prob_win
    else:
        double_step = 2 * curr_wealth
        cache[curr_wealth] = prob_win * recursive_win_probability(
            double_step, max_wealth, prob_win, prob_loss, cache, max_depth, depth + 1
        ) + prob_loss * recursive_win_probability(0, max_wealth, prob_win, prob_loss, cache, max_depth, depth + 1)

    return cache[curr_wealth]

def recursive_game_duration(curr_wealth, max_wealth, prob_win, prob_loss, cache, max_depth, depth=0):
    """
    Recursive helper to calculate the expected duration of the game starting from wealth curr_wealth with depth limit.
    """
    if curr_wealth == 0 or curr_wealth >= max_wealth or depth >= max_depth:
        return 0.0  

    if curr_wealth in cache:
        return cache[curr_wealth]

    if curr_wealth >= max_wealth / 2:
        half_step = 2 * curr_wealth - max_wealth
        if half_step >= 0:
            cache[curr_wealth] = 1 + prob_loss * recursive_game_duration(
                half_step, max_wealth, prob_win, prob_loss, cache, max_depth, depth + 1
            )
        else:
            cache[curr_wealth] = 1 / prob_win
    else:
        double_step = 2 * curr_wealth
        if double_step <= max_wealth:
            cache[curr_wealth] = 1 + prob_win * recursive_game_duration(
                double_step, max_wealth, prob_win, prob_loss, cache, max_depth, depth + 1
            ) + prob_loss * recursive_game_duration(0, max_wealth, prob_win, prob_loss, cache, max_depth, depth + 1)
        else:
            cache[curr_wealth] = 1 / prob_win

    return cache[curr_wealth]

def win_probability(p, q, k, N):
    """
    Return the probability of winning while gambling aggressively, with recursion depth based on binary precision.
    
    Parameters:
    - p: float, 0 < p < 1, probability of winning a round
    - q: float, q = 1 - p, probability of losing a round
    - k: int, starting wealth
    - N: int, maximum wealth
    - k_prec: int, maximum bits after the decimal for binary representation

    Returns:
    - float, probability of reaching wealth N starting from k
    """
    k_prec=16
    # Only use k_prec when N is not a power of 2 and k is neither 0, N, nor N/2
    if not is_power_of_2(N) and k not in {0, N, N // 2}:
        binary_rep = decimalToBinary(k / N, k_prec)
        max_depth = len(binary_rep.split('.')[1])  # Get the number of bits in the fractional part
    else:
        max_depth = float('inf')  # No recursion depth limit in this case

    cache = {}
    return recursive_win_probability(k, N, p, q, cache, max_depth)

def game_duration(p, q, k, N):
    """
    Return the expected number of rounds to either win or get ruined while gambling aggressively,
    with recursion depth based on binary precision.
    
    Parameters:
    - p: float, 0 < p < 1, probability of winning a round
    - q: float, q = 1 - p, probability of losing a round
    - k: int, starting wealth
    - N: int, maximum wealth
    - k_prec: int, maximum bits after the decimal for binary representation
    
    Returns:
    - float, expected number of rounds to reach N or 0 starting from k
    """
    k_prec=16
    # Only use k_prec when N is not a power of 2 and k is neither 0, N, nor N/2
    if not is_power_of_2(N) and k not in {0, N, N // 2}:
        binary_rep = decimalToBinary(k / N, k_prec)
        max_depth = len(binary_rep.split('.')[1])  # Get the number of bits in the fractional part
    else:
        max_depth = float('inf')  # No recursion depth limit in this case

    cache = {}
    return recursive_game_duration(k, N, p, q, cache, max_depth)

    





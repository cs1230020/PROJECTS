def game_duration(p, q, k, t, W):
    
    if p != q:
        
        o = 1 / (q - p)
        return (k - t) * (o + (1 - o) * (p / q) ** W)
        
    else:
        
        return (2 * W + 1) * (k - t)



    


def countTransactionSequences(n, k, m):
    mem = dict()
    
    def rec(current, buys, sells):
        if (current, buys, sells) in mem: return mem[(current, buys, sells)]
        if current<0: return 0

        total = 0
        if current==n:
            total+=1
        if buys+sells==m: return total
        
        buy = rec(current+1, buys+1, sells)
        total+=buy
        if (current+1, buys+1, sells) not in mem: mem[(current+1, buys+1, sells)] = buy
        
        sell = rec(current-1, buys, sells+1)
        total+=sell
        if (current-1, buys, sells+1) not in mem: mem[(current-1, buys, sells+1)] = sell
        
        return total
    
    return rec(k, 0, 0)

if __name__=="__main__":
    n, k, m = 0, 0, 2
    res = countTransactionSequences(n, k, m)
    print(res)
    
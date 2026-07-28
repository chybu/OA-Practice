def countTransactionSequences(n, k, m):
    mem = dict()
    
    def rec(current, operations):
        if (current, operations) in mem: return mem[(current, operations)]
        if current<0: return 0

        total = 0
        if current==n:
            total+=1
        if operations==m: return total
        
        buy = rec(current+1, operations+1)
        total+=buy
        if (current+1, operations+1) not in mem: mem[(current+1, operations+1)] = buy
        
        sell = rec(current-1, operations+1)
        total+=sell
        if (current-1, operations+1) not in mem: mem[(current-1, operations+1)] = sell
        
        return total
    
    return rec(k, 0)

if __name__=="__main__":
    n, k, m = 0, 0, 1000
    res = countTransactionSequences(n, k, m)
    print(res)
    
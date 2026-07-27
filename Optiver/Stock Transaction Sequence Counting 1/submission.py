def countTransactionSequences(n:int) -> int:
    """
    pretend buy = 1 and sell = -1
    mission is try to have n number of buy and n number of sell so that the sum from left to right never <0
    
    """
    
    mem = dict()
    
    def rec(total, buys, sells):
        
        if (total, buys, sells) in mem:
            return mem[(total, buys, sells)]
        
        if total<0: return 0
        if buys>n: return 0
        if sells>n: return 0
        
        if buys==n and sells==n: return 1
        
        buy = rec(total+1, buys+1, sells)
        if (total+1, buys+1, sells) not in mem: mem[(total+1, buys+1, sells)] = buy
        
        sell = rec(total-1, buys, sells+1)
        if (total-1, buys, sells+1) not in mem: mem[(total-1, buys, sells+1)] = sell
        
        return buy + sell

    return rec(0, 0, 0)

if __name__=="__main__":
    n = 60
    res = countTransactionSequences(n)
    
    print(res)
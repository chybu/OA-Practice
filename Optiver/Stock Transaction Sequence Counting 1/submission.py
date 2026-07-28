# recursion
# def countTransactionSequences(n:int) -> int:
#     """
#     pretend buy = 1 and sell = -1
#     mission is try to have n number of buy and n number of sell so that the sum from left to right never <0
    
#     """
    
#     mem = dict()
    
#     def rec(total, buys, sells):
        
#         if (total, buys, sells) in mem:
#             return mem[(total, buys, sells)]
        
#         if total<0: return 0
#         if buys>n: return 0
#         if sells>n: return 0
        
#         if buys==n and sells==n: return 1
        
#         buy = rec(total+1, buys+1, sells)
#         if (total+1, buys+1, sells) not in mem: mem[(total+1, buys+1, sells)] = buy
        
#         sell = rec(total-1, buys, sells+1)
#         if (total-1, buys, sells+1) not in mem: mem[(total-1, buys, sells+1)] = sell
        
#         return buy + sell

#     return rec(0, 0, 0)

# iterative
def countTransactionSequences(n:int) -> int:
    if n==0: return 1
    mem = [[0]*(n+1) for i in range (2*n+1)]
    mem[1][1] = 1
    for move in range(2, len(mem)):
        for total in range(n+1):
            val = 0
            before_buy = total-1
            if before_buy>=0:
                val+=mem[move-1][before_buy]
                
            before_sell = total+1
            if before_sell<=n:
                val+=mem[move-1][before_sell]
            
            mem[move][total] = val
            
    return mem[-1][0]         

if __name__=="__main__":
    n = 60
    res = countTransactionSequences(n)
    
    print(res)
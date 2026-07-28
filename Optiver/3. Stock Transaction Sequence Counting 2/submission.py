# recursion version
# def countTransactionSequences(n, k, m):
#     mem = dict()
    
#     def rec(current, operations):
#         if (current, operations) in mem: return mem[(current, operations)]
#         if current<0: return 0

#         total = 0
#         if current==n:
#             total+=1
#         if operations==m: return total
        
#         buy = rec(current+1, operations+1)
#         total+=buy
#         if (current+1, operations+1) not in mem: mem[(current+1, operations+1)] = buy
        
#         sell = rec(current-1, operations+1)
#         total+=sell
#         if (current-1, operations+1) not in mem: mem[(current-1, operations+1)] = sell
        
#         return total
    
#     return rec(k, 0)

# iterative version
def countTransactionSequences(n, k, m):
    mem = [[0]*(k+m+1) for i in range(m+1)]
    mem[0][k] = 1
    MAX_BUY = k+m
    if MAX_BUY<n: return 0
    for move in range(1, m+1):
        for total in range(0, MAX_BUY+1):
            val = 0
            before_buy = total-1
            if before_buy>=0:
                val+=mem[move-1][before_buy]
            
            before_sell = total+1
            if before_sell<=MAX_BUY:
                val+=mem[move-1][before_sell]
                
            mem[move][total] = val
        
    return sum([move[n] for move in mem])
    
    
if __name__=="__main__":
    n, k, m = 10, 0, 9
    res = countTransactionSequences(n, k, m)
    print(res)
    
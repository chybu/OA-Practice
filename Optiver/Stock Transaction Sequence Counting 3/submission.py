
# recursion version
# def countTransactionSequences(n:int, k:list) -> int:
#     mem = dict()
    
#     def rec(current, operations):
#         if (current, operations) in mem: return mem[(current, operations)]
        
#         if current>n: return 0
#         if current==n: return 1
        
#         total = 0
#         for num in k:
#             val = rec(current+num, operations)
#             total+=val
#             if (current+num, operations) not in mem:
#                 mem[(current+num, operations)] = val
                
#         return total
    
    
#     return rec(0, 0)

# iterative version
def countTransactionSequences(n:int, k:list) -> int:
    "giving number n and a list of numbers k, find how many combinations only use numbers in k and the sum of them is n"
    mem = [0]*(n+1)
    mem[0] = 1
    for sum in range(1, n+1):
        total = 0
        for last_num in k:
            if sum-last_num<0: continue
            total+=mem[sum-last_num]
        mem[sum] =total
        
    return mem[n]
            

if __name__ == "__main__":
    n, k = 5, [1, 2]
    
    res = countTransactionSequences(n, k)
    print(res)
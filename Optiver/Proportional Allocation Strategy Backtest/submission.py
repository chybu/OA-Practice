import math

def BacktestStatistics(
    timeseries: list[list[float]],
) -> list[float]:
    
    """
    Given some money, try to buy/sell stock based on its performance and record the log return
    
    Return = growth rate = current val / yesterday val
    in day 0, since there is no yesterday val, return = 1 means the same
    
    At the end of day 1:
    
    
    stock 1 price increases 15%
    stock 2 price increases 5% 
    total increases = 20%
    
    what is the total money? It can come from two sources:
    1. cash
    2. existing stocks
    Since it's day 1, money is from cash = 1M
    
    15% is 75% of 20% => allocate 75% of 1M to stock 1
    => allocate 25% of 1M to stock 2
    
    stock 1: 750K
    stock 2: 250K
    
    the default yesterday val is 1M
    => return = .....
    update yesterday val
    
    At the end of day 2:
        
    stock 1 price increases 2%
    stock 2 price decreases 5%
    
    Since we have stock, so the money come from stock:
        current val = 750K*(117.3/115) + 250K*(199.5/210) = 1,002,500
        
    
    => 1,002,500 goes all to stock 1
    
    
    pseudo code:
    yesterday_val = 1M
    cash = 1M
    allocate_dic = dic() showing owned stock and their val
    
    Iterate from day 1
    
    total_increase = 0
    change_dic
    Iterate thru each stock
    
    if the price > yesterday price
        total_increase+= (price/yesterday price) - 1
        change_dic[id] = (price/yesterday price) - 1
    elif id in allocate_dic:
        change_dic[id] = (price/yesterday price) - 1
    
    # calculate total money to reallocate
    if cash:
        current_val = cash
    else:
        for id, allocate_amount in allocate_dic.items():
            current_val += allocate_amount * (change_dic[id]+1)
            # if the stock doesn't increase, then will sell it => don't need to keep track
            if change_dic[id]<=0:
                allocate_dic.pop(id) 
    
    # reallocate
    if total_increase==0 or no increase:
        cash = current_val
    else:
        cash = 0
        for id, change_percent in change_dic.items():
            if change_percent>0:
                allocate_dic[id] = change_percent/total_increase * current_val
    
    return = current_val/yesterday_val
    update return list
    """
    
    yesterday_val = 1_000_000
    cash = 1_000_000
    allocate_dic = dict()
    return_log_list = []
    
    for day in range(1, len(timeseries[0])):
        total_increase = 0
        change_dic = dict()
        # calculate the change amount of good stock and owning stock
        for id, stock in enumerate(timeseries):
            if stock[day]>stock[day-1]:
                change = (stock[day]/stock[day-1]) - 1
                total_increase+=change
                change_dic[id] = change
            elif id in allocate_dic:
                change_dic[id] = (stock[day]/stock[day-1]) - 1
        # calculate total amount of money to rebalance
        if cash:
            current_val = cash
        else:
            current_val = 0
            pop_list = []
            for id, allocate_amount in allocate_dic.items():
                current_val += allocate_amount*(change_dic[id]+1)
                # remove bad stock from owning
                if change_dic[id]<=0:
                    pop_list.append(id)
            for id in pop_list:
                allocate_dic.pop(id)
            
        # rebalance
        if total_increase==0:
            cash = current_val
        else:
            cash = 0
            for id, change in change_dic.items():
                if change>0:
                    allocate_dic[id] = (change/total_increase) * current_val
                
        return_log_list.append(
            math.log(current_val/yesterday_val)
        )
        yesterday_val = current_val
        
    mean = sum(return_log_list)/ len(return_log_list)
    variances = []
    for log in return_log_list:
        variances.append(
            (log-mean)**2
        )
    std = math.sqrt(sum(variances) / len(return_log_list))
    return [mean, std]


if __name__ == "__main__":
    example = [[100.0, 110.0, 132.0], 
               [50.0, 55.0, 49.5]]

    result = BacktestStatistics(example)
    print(result)
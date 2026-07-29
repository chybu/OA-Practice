import heapq

"""
1. 0 is the deepest level. The biggest level is the topmost
2. let say the level is X. then the size of the level is the Xth number in the fibonanci chain
3. 
"""

def fibonanci(n, dic):
    if n in dic: return dic[n]
    if n == 0: return 1
    if n == 1: return 2
    
    val = fibonanci(n-1, dic) + fibonanci(n-2, dic)
    dic[n] = val
    return val

def remove_stale(target, token_set):
    while target[0][3] not in token_set:
        heapq.heappop(target)
    
    
class Storage:
    def __init__(self, max_size, level):
        # for redistribute the location
        self.min_heap = []
        # for retrive nuts
        self.max_heap = []
        self.size = 0
        self.max_size = max_size
        self.level = level
        self.token_set = set()
        
    def is_full(self):
        return self.size==self.max_size
    
    def is_empty(self):
        return self.size==0
    
    def is_haft(self):
        return self.size<self.max_size/2
    
    def __str__(self):
        return (
            f"min_heap: {self.min_heap} "
            f"max_heap: {self.max_heap} "
            f"size: {self.size} "
            f"max size: {self.max_size} "
        )



class SquirrelResearch:
    def __init__(self, locations:dict[str, int]):
        self.location_dic:dict[str, list[Storage]] = dict()
        size_dic = dict()
        for id, size in locations.items():
            level_list = []
            for level in range(size):
                max_size = fibonanci(level, size_dic)
                level_list.append(Storage(max_size, level))
            self.location_dic[id] = level_list
                    
        self.nuts_set = set()
        self.token_counter = 0
        
    def HideNut(
        self,
        timestamp:float,
        location_id:str,
        nut_id:str,
        nut_weight:float,
        time_to_expire:float,
    )->bool:
        if location_id not in self.location_dic: return False
        if nut_id in self.nuts_set: return False
        
        levels = self.location_dic[location_id]
        if levels[-1].is_full(): return False
        
        for storage in levels:
            if storage.is_full(): continue
            heapq.heappush(storage.min_heap, (nut_weight, nut_id, timestamp+time_to_expire, self.token_counter))
            heapq.heappush(storage.max_heap, (-nut_weight, nut_id, timestamp+time_to_expire, self.token_counter))
            storage.token_set.add(self.token_counter)
            self.token_counter+=1
            self.nuts_set.add(nut_id)
            storage.size+=1
            break
            
        return True
    
    def RetrieveNuts(
        self,
        timestamp: float,
        location_id: str,
        max_squirrel_capacity_in_nuts:int,
    ) ->list:
        
        """
        reachable condition:
        the topmost with >0 nuts is reachable
        from the topmost, if it is <50% occupied, then topmost level -1  is also reachable
        due to the redistribute mechanism and the hidnut mechanism, only need to care about the topmost and possibly topmost -1 level
        
        """
        
        
        if location_id not in self.location_dic: return []
        
        res = []
        levels = self.location_dic[location_id]
        
        while len(res)<max_squirrel_capacity_in_nuts and not levels[0].is_empty():
            for level in range(len(levels)-1, -1, -1):
                storage = levels[level]
                
                if storage.is_empty(): continue
                
                if storage.level>0 and storage.is_haft():
                    remove_stale(storage.max_heap, storage.token_set)
                    nut_weight_1, nut_id_1, expire_1, token1 = storage.max_heap[0]
                    
                    sub_storage = levels[level-1]
                    remove_stale(sub_storage.max_heap, sub_storage.token_set)
                    nut_weight_2, nut_id_2, expire_2, token2 = sub_storage.max_heap[0]
                    
                    need_redistribute = False
                    
                    if nut_weight_1==nut_weight_2 and nut_id_1>nut_id_2:
                        need_redistribute = True
                    elif -nut_weight_1<-nut_weight_2:
                        need_redistribute = True
                                        
                    if need_redistribute:
                        if expire_2>=timestamp:
                            res.append(nut_id_2)
                        heapq.heappop(sub_storage.max_heap)
                        self.nuts_set.remove(nut_id_2)
                        sub_storage.token_set.remove(token2)
                        
                        remove_stale(storage.min_heap, storage.token_set)
                        new_nut = heapq.heappop(storage.min_heap)
                        storage.size-=1
                        storage.token_set.remove(token1)
                        sub_storage.token_set.add(token1)
                        
                        heapq.heappush(sub_storage.max_heap, (-new_nut[0], new_nut[1], new_nut[2], new_nut[3]))
                        heapq.heappush(sub_storage.min_heap, new_nut)
                    else:
                        if expire_1>=timestamp:
                            res.append(nut_id_1)
                        heapq.heappop(storage.max_heap)
                        storage.size-=1
                        self.nuts_set.remove(nut_id_1)
                        storage.token_set.remove(token1)
                    
                else:
                    remove_stale(storage.max_heap, storage.token_set)
                        
                    nut_weight, nut_id, expire, token = heapq.heappop(storage.max_heap)
                    storage.size-=1
                    self.nuts_set.remove(nut_id)
                    storage.token_set.remove(token)
                    if expire>=timestamp:
                        res.append(nut_id)
                
                break
        return res
    
if __name__=="__main__":
    research = SquirrelResearch({"oak": 3})
    research.HideNut(1.0, "oak", "level0", 1.0, 100.0)
    research.HideNut(2.0, "oak", "level1-heavy", 9.0, 100.0)
    research.HideNut(3.0, "oak", "level1-light", 2.0, 100.0)
    research.HideNut(4.0, "oak", "level2", 5.0, 100.0)
    research.RetrieveNuts(5.0, "oak", 1)
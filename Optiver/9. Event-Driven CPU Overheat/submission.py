import math

"""
temperature, temperature rate and load is different. Temperature is calculated from load


a core has some attribute:
    status: run or die
    load
    temp increase rate
    prev_temp
    prev_sec
    
controller:
    core_dic
    sorted_core_oder
    changed_set to capture setCoreLoad change
    
what if set core load 2 times?
=> whenever set core load, calculate current temp
    if current temp >=shutdownTemp, prev_temp=0
    else prev_temp = current temp
    
When calling Tick, will inspect the entire core again and clear the changed_set

The hard part is that needs to recalculate the temp_rate whenever a core change state

"""

class Core:
    def __init__(self, id, cool):
        self.id = id
        self.load = 0
        self.cool = cool
        self.running = True
        self.temp_rate = 0
        self.temp = 0

class CPUController:
    def __init__(self, pooledCooling, coreIds, activeCooling, shutdownTemperature):
        self.core_dic:dict[int, Core] = dict()
        for id, cool in zip(coreIds, activeCooling):
            self.core_dic[id] = Core(id, cool)
            
        self.changed_set = set()
        self.time = 0
        self.shutdownTemp = shutdownTemperature
        self.pool_cool = pooledCooling
        self.running_core = len(coreIds)
    
    def move_to_target_time(self, target_time):
        while self.time!=target_time:
            need_to_move = target_time-self.time
            for core in self.core_dic.values():
                if not core.running or core.temp_rate<=0: continue
                second_before_shutdown = int(math.ceil((self.shutdownTemp-core.temp)/core.temp_rate))
                need_to_move = min(need_to_move, second_before_shutdown)
            shutdown = False
            
            for core in self.core_dic.values():
                if not core.running: continue
                core.temp = max(0, core.temp + core.temp_rate*need_to_move) 
                if core.temp>=self.shutdownTemp:
                    core.running = False
                    self.changed_set.add(core.id)
                    shutdown = True
                    self.running_core-=1
                    
            if shutdown:
                self.update_temp_rate()
                
            self.time+=need_to_move
        

    def get_temp_rate(self, core:Core):            
        return core.load - core.cool - math.floor(self.pool_cool / self.running_core)
            
    def update_temp_rate(self):       
        for core in self.core_dic.values():
            if not core.running: continue
            core.temp_rate = self.get_temp_rate(core)
    
    def SetCoreLoad(self, timestamp, coreId, watts):
        
        self.move_to_target_time(timestamp)
        core = self.core_dic[coreId]
        core.load = watts
        
        if not core.running:
            self.changed_set.add(coreId)
            core.running = True
            core.temp = 0
            self.running_core+=1
            
            self.update_temp_rate()
        else:
            core.temp_rate = self.get_temp_rate(core)
            

            
    def Tick(self, timestamp):
        self.move_to_target_time(timestamp)
        
        res = sorted(list(self.changed_set))
        self.changed_set.clear()
        return res
        
        
def simulateOverheatController(
    pooledCooling: int,
    coreIds: list[int],
    activeCooling: list[int],
    shutdownTemperature: int,
    operations: list[str],
    operationData: list[list[int]]
) -> list[list[int]]:
    
    controller = CPUController(pooledCooling, coreIds, activeCooling, shutdownTemperature)
    
    res = []
    for operation, data in zip(operations, operationData):
        if operation=="Tick":
            res.append(
                controller.Tick(data[0])
            )
        else:
            controller.SetCoreLoad(data[0], data[1], data[2])
            
    return res
    
if __name__=="__main__":
    # pooledCooling = 3
    # coreIds = [1]
    # activeCooling = [2]
    # shutdownTemperature = 5
    # operations = [
    #     "SetCoreLoad", "Tick", "SetCoreLoad", "Tick",
    #     "SetCoreLoad", "Tick", "SetCoreLoad", "Tick"
    # ]
    # operationData = [
    #     [0, 1, 6], [1], [1, 1, 0], [3],
    #     [3, 1, 10], [4], [4, 1, 4], [5]
    # ]
    # simulateOverheatController(pooledCooling, coreIds, activeCooling, shutdownTemperature, operations, operationData)
    simulateOverheatController(2,
                    [1, 2],
                    [0, 0],
                    1_000_000_000,
                    ["SetCoreLoad", "SetCoreLoad", "Tick"],
                    [
                        [0, 1, 3],
                        [0, 2, 2],
                        [1_000_000_000],
                    ],)
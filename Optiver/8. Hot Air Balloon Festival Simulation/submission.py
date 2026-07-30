"""
1. maintain the original order
2. when the wind speed is set, then need to recalculate the speed of the exising altitude

"""

class Balloon:
    def __init__(self, name):
        self.recover_start = None
        self.stable = True
        self.name = name
        self.altitude = 0
        self.total_wind = None

class BalloonFestival:
    def __init__(self, balloonNames:list[str]):
        self.original_order = balloonNames
        self.wind_dic = dict()
        self.balloon_dic:dict[str, Balloon] = dict()
        for name in balloonNames:
            self.balloon_dic[name] = Balloon(name)
        self.current_timestamp = -1
    
    def calculate_total_wind(self, altitude):
        res = 0
        for centerAltitude, windspeed in self.wind_dic.items():
            res += windspeed / (1 + ((altitude - centerAltitude) / 100) ** 2)
        
        return res
        
    def balloon_ascended(self, timestamp, name, altitude):
        if timestamp<=self.current_timestamp: return False        
        if name not in self.balloon_dic: return False
        
        self.current_timestamp = timestamp
                
        balloon = self.balloon_dic[name]
        
        if altitude==balloon.altitude: return True
        
        total_wind = self.calculate_total_wind(altitude)
        
        balloon.altitude = altitude
        balloon.total_wind = total_wind
        
        if total_wind>15:
            balloon.stable = False
            balloon.recover_start = None
        else:
            balloon.recover_start = timestamp
            
        return True
    
    def balloon_descended(self, timestamp, name):
        if timestamp<=self.current_timestamp: return False
        if name not in self.balloon_dic: return False
        
        balloon = self.balloon_dic[name]
        
        if balloon.altitude==0: return False
        
        self.current_timestamp = timestamp
        
        balloon.altitude = 0
        balloon.stable = True
        
        return True
    
    def set_wind_speed(self, timestamp, centerAltitude, windSpeed):
        if timestamp<=self.current_timestamp: return False
                
        self.current_timestamp = timestamp
        
        self.wind_dic[centerAltitude] = windSpeed        
        for balloon in self.balloon_dic.values():
            if balloon.altitude==0: continue
            total_wind = self.calculate_total_wind(balloon.altitude)
            balloon.total_wind = total_wind
            """
            if new wind is not stable => balloon not stable
            if new wind is stable
                if start_recover is None => start recover
                else keep the old start recover
            """
            
            if total_wind>15:
                balloon.stable = False
                balloon.recover_start = None
            elif balloon.recover_start is None:
                balloon.recover_start = timestamp
                
        return True
                
    def inspect_balloons(self, timestamp):
        if timestamp<=self.current_timestamp: return []
                        
        self.current_timestamp = timestamp
        
        res = []
        max_altitude = 0
        for name in self.original_order:
            balloon = self.balloon_dic[name]
            if balloon.altitude==0: continue
            if balloon.altitude<max_altitude: continue
            
            if balloon.stable:
                if balloon.altitude==max_altitude:
                    res.append(name)
                else:
                    res = [name]
                    max_altitude = balloon.altitude
            elif (balloon.recover_start is not None and timestamp-balloon.recover_start>=300):
                balloon.stable = True
                if balloon.altitude==max_altitude:
                    res.append(name)
                else:
                    res = [name]
                    max_altitude = balloon.altitude
        
        return res

if __name__=="__main__":
    festival = BalloonFestival(["Aurora", "Comet"])

    print(festival.balloon_ascended(10, "Aurora", 100))
    # returns True

    print(festival.balloon_ascended(20, "Comet", 200))
    # returns True

    print(festival.inspect_balloons(30))
    # returns ["Comet"]

    print(festival.set_wind_speed(40, 200, 20))
    # returns True

    print(festival.inspect_balloons(50))
    # returns ["Aurora"]
import heapq
from collections import deque

def match(l1, l2):
    for i in l2:
        if i in l1: return True
    
    return False

class Subscriber:
    def __init__(self, id=None, minInterest=None, maxNewsPerSecond=None, topics=None):
        self.id = id
        self.minInterest = minInterest
        self.maxNewsPerSecond = maxNewsPerSecond
        self.topics = topics
        self.seen_news = set()
        self.time_q = deque()
        
    def rate_check(self, upper):
        lower = upper-1
        while self.time_q and self.time_q[0]<=lower:
            self.time_q.popleft()
            
        return len(self.time_q)<self.maxNewsPerSecond        

class News:
    def __init__(self, id=None, timestamp=None, interest=None, topics=None):
        self.id = id
        self.timestamp = timestamp
        self.interest = interest
        self.topics = topics
        
class NewsProvider:
    def __init__(self):
        self.subscriber_dic: dict[int, Subscriber] = dict()
        self.news_dic: dict[int, News] = dict()
    
    def AddSubscription(self, id, minInterest, maxNewsPerSecond, topics):
        if id not in self.subscriber_dic:
            subscriber = Subscriber()
            self.subscriber_dic[id] = subscriber
        else:
            subscriber = self.subscriber_dic[id]
        
        subscriber.id = id
        subscriber.minInterest = minInterest
        subscriber.maxNewsPerSecond = maxNewsPerSecond
        subscriber.topics = topics
                
        return True
    
    def RemoveSubscription(self, id):
        if id not in self.subscriber_dic: return False
        self.subscriber_dic.pop(id)
        return True
    
    
    def NewsReceived(self, id, timestamp, interest, topics):
        if id in self.news_dic: return False
        
        self.news_dic[id] = News(id, timestamp, interest, topics)
        return True

    def Publish(self, timestamp, maxAge):
        """
        don't give the same news to the subscriber
        check the rate limit
        return a dict, where keys are the news id and the value are the list of the news subscriber
        
        filter out valid age news and not in future => list of news.
        put the news in a max heap with interest score, bigger age, bigger id
        for each news
            for each customer in the customer heap
                customer nver seen this before
                matching interest
                matching topic
                valid rate limit
        
        """
        
        max_heap = []
        for news in self.news_dic.values():
            age = timestamp-news.timestamp
            if age<0 or age>maxAge: continue
            
            heapq.heappush(max_heap, (-news.interest, news.timestamp, -news.id))
            
        res = dict()
        while max_heap:
            new_id = -heapq.heappop(max_heap)[2]
            news = self.news_dic[new_id]
            for subscriber in self.subscriber_dic.values():
                if news.id in subscriber.seen_news: continue
                if news.interest < subscriber.minInterest: continue
                if not match(news.topics, subscriber.topics): continue
                if not subscriber.rate_check(timestamp): continue
                
                subscriber.seen_news.add(news.id)
                subscriber.time_q.append(timestamp)
                
                if news.id not in res:
                    res[news.id] = []
                    
                res[news.id].append(subscriber.id)
                
        final_res = dict()
        for news_id, sub_list in res.items():
            final_res[news_id] = sorted(sub_list)
            
        return final_res
                
                
                
        

        
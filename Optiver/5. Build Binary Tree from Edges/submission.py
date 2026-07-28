from collections import deque

class Node:
    def __init__(self, letter):
        self.val = letter
        self.l = None
        self.r = None

def buildSExpression(pairs:list[str])->str:
    """
    check the lowest error to the highest error
    
    E1: check for string format
    
    E2: build a set and check if the current pair is already in the set
    
    E3: build a dic of node with letter as key.
    Access the parrent node in the dic and check if the left and right is not None
    If both of them is not None => E3
    If one of them is not None then check if they are in the correct order.
    Like left lex order should be smaller than right lex order. If not then switch
    If both is None then use the left one
    
    E4: Multiple roots or one child two parents
    Create a set of key of the node dic
    Create a parented set
    Iterate thru the node
    Remove the children node.val out of the key_set
    Add the children node.val to the parented set. if the children node.val is in it => E4
    Check if the final size of the key_set is 1. That's one is the root
    
    Notice that E4 can also cath circle loop with one parent restriction: (A,B), (B,D), (D,B)
    The circle types E4 cannot catch is a isolated circle
    
    E5: Create a visted set
    BFS the tree. 
    If the visted size != size of the keys of the dict => cycle => E5
    
    """
    if not pairs: return "E1"
    valid_range = range(ord("A"), ord("Z")+1)
    def check1(s):
        if len(s)!=5 or s[0]!="(" or s[-1]!=")" or  s[2]!="," or ord(s[1]) not in valid_range or ord(s[3]) not in valid_range: return False
        return True
    
    pairs_set = set()
    node_dic = dict()
    E2 = False
    E3 = False
    for s in pairs:
        if not check1(s): return "E1"
        pair = (s[1], s[3])
        # check E2
        if pair in pairs_set: E2 = True
        pairs_set.add(pair)
        
        if s[1] not in node_dic:
            node_dic[s[1]] = Node(s[1])
        if s[3] not in node_dic:
            node_dic[s[3]] = Node(s[3])
        
        # check E3
        parent_node = node_dic[s[1]]
        child_node = node_dic[s[3]]
        if parent_node.l is not None and parent_node.r is not None: E3=True
        if parent_node.l is None and parent_node.r is None:
            parent_node.l = child_node
        else:
            if ord(parent_node.l.val)>ord(child_node.val):
                parent_node.r = parent_node.l
                parent_node.l = child_node
            else:
                parent_node.r = child_node
    
    if E2: return "E2"
    if E3: return "E3"
        
    # check E4     
    key_set = set(node_dic.keys())
    parented = set()
    for key, node in node_dic.items():
        if node.l is not None:
            if node.l.val in parented: return "E4"
            key_set.remove(node.l.val)
            parented.add(node.l.val)
        if node.r is not None:
            if node.r.val in parented: return "E4"
            key_set.remove(node.r.val)
            parented.add(node.r.val)
            
    if len(key_set)>1: return "E4"
    if len(key_set)==0: return "E5"
    
    root = node_dic[key_set.pop()]
    
    # check E5
    visited = 0
    dq = deque()
    dq.append(root)
    while dq:
        for i in range(len(dq)):
            node = dq.popleft()
            visited+=1
            if node.l is not None:
                dq.append(node.l)
            if node.r is not None:
                dq.append(node.r)
                
    if visited!=len(node_dic): return "E5"
    
    
    # Build the S-Expression
    def rec(node:Node):
        if node is None: return ""
        
        return f"({node.val}{rec(node.l)}{rec(node.r)})"
        
    return rec(root)
        
if __name__=="__main__":
    pairs = ["(A,B)", "(B,C)", "(A,D)"]
    res = buildSExpression(pairs)
    print(res)
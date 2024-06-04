import socket

class Msg:
    '''message object'''
    msg_type: str
    node_id: str
    curr_round: str
    dv: []
    changed: str
    converged: str

    def __init__(self, msg_type, node_id, curr_round, dv, changed, converged):
        self.msg_type = msg_type
        self.node_id = node_id
        self.dv = dv
        self.curr_round = curr_round
        self.changed = changed
        self.converged = converged

    def pack(self):
        res = []
        res.append(self.msg_type)
        res.append(self.node_id)
        res.append(str(self.curr_round))
        res.append(self.changed)
        res.append(self.converged)
        res.append(self.to_string())
        return ' '.join(res)
    
    def to_string(self):
        return ' '.join(str(i) for i in self.dv)

def unpack(data):
    string = data.decode('utf-8')
    string = string.split()
    msg_type = string[0]
    node_id = string[1]
    curr_round = string[2]
    changed = string[3]
    converged = string[4]
    dv = string[5:]
    return (msg_type, node_id, curr_round, changed, converged, dv)

    

def send_msg(addr, msg, wait):
    #print(f"host is {addr[0]} and port being sent to is {addr[1]} from node {node_id}")
    #print(f"the msg is {msg}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send:
        #print(f"{addr} just before connect")
        send.connect(addr)
        #print(msg.encode('utf-8'))
        send.sendall(msg.encode('utf-8'))
        if wait:
            send.recv(1024)
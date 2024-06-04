import socket
import time
import msg as m


def node(vals):
    host = "127.0.0.1"
    node_id, port, barr, start, dv, node_list, lock, output_file = vals
    sendlist = create_sendlist(node_list, dv)
    curr_round = 1
    changed = 'false'
    old_dv = []
    converged = '0'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        barr.wait(10)
        s.listen(20)
        if start:
            print("Round 1: A\n")
            print(f"Current DV matrix = {dv}\n")
            print("Last DV matrix = none\n")
            print("Updated from last DV matrix or the same? Updated\n")
            output_file.write("Round 1: A\n")
            output_file.write(f"Current DV matrix = {dv}\n")
            output_file.write("Last DV matrix = none\n")
            output_file.write("Updated from last DV matrix or the same? Updated\n\n")
            init(sendlist, host, dv, node_id, changed, output_file, converged)
            start = False

        while True:
            conn, _ = s.accept()
            #time.sleep(3)
            with conn:
                #print(f"Port {port} connected with {addr}")
                data = conn.recv(1024)
                if not data:
                    print(f"node {node} received an empty message\n")
                    break
                #print(data)
                msg_data = m.unpack(data)
                msg = m.Msg(msg_data[0], msg_data[1], msg_data[2], msg_data[5], msg_data[3], msg_data[4])
                curr_round = msg.curr_round
                converged = msg.converged
                match msg.msg_type:
                    case 'update':
                        lock.acquire()
                        old_dv = dv.copy()
                        changed = print_update(node_id, dv, msg.node_id, msg.dv, sendlist, port, old_dv, output_file)
                        
                        conn.sendall(b'ok')
                        lock.release()
                    case 'run':
                        if changed == 'false':
                            old_dv = dv.copy()
                        dv = calc_distance(msg.dv, dv, sendlist, port)
                        print(f"Round {curr_round}: {node_id}")
                        print(f"Current DV matrix {dv}")
                        print(f"Last DV matrix = {old_dv}")
                        print(f"Updated from last DV matrix or the same? {'Updated' if changed =='true' else 'Same'}\n")
                        #changed = 'true' if msg.changed or changed else 'false'
                        output_file.write(f"Round {curr_round}: {node_id}\n")
                        output_file.write(f"Current DV matrix {dv}\n")
                        output_file.write(f"Last DV matrix = {old_dv}\n")
                        output_file.write(f"Updated from last DV matrix or the same? {'Updated' if changed == 'true' else 'Same'}\n\n")

                        for dest in sendlist:
                            msg = m.Msg('update', node_id, curr_round, dv, changed, converged)
                            print(f"Sending DV to node {dest[0]}")
                            output_file.write(f"Sending DV to node {dest[0]}\n")
                            m.send_msg((host, dest[1]), msg.pack(), True)
                        if port == 2004:
                            if msg.changed != 'true':
                                msg = m.Msg('end', '0', curr_round, dv, '0', converged)
                                print("Final output:")
                                m.send_msg((host, 2000), msg.pack(), False)
                            else:
                                changed = 'false'

                            if changed == 'true':
                                converged = curr_round
                            msg = m.Msg('run', node_id, str(int(curr_round) + 1), dv, changed, converged)
                            m.send_msg((host, 2000), msg.pack(), False)
                        else:
                            if changed == 'true':
                                converged = curr_round
                            msg = m.Msg('run', node_id, str(int(curr_round) + 1), dv, changed, converged)
                            m.send_msg((host, port + 1), msg.pack(), False)
                    case 'end':
                        print(f"Node {node_id} DV = {dv}")
                        output_file.write(f"Node {node_id} DV = {dv}\n")
                        msg = m.Msg('end', '0', converged, dv, '0', converged)
                        if port != 2004:
                            m.send_msg((host, port + 1), msg.pack(), False)
                        if port == 2004:
                            print(f"Number of rounds until convergence = {converged}")
                            output_file.write(f"Number of rounds until convergence = {converged}\n")
                            output_file.write("-------------------------------------------------------------------------\n\n")
                        break

def init(sendlist, host, dv, node_id, changed, output_file, converged):
    for dest in sendlist:
        msg = m.Msg('update', node_id, 1, dv, changed, converged)
        print(f"Sending DV to node {dest[0]}")
        output_file.write(f"Node {node_id} DV = {dv}\n")
        m.send_msg((host, dest[1]), msg.pack(), True)
    mesg = m.Msg('run', node_id, 2, dv, changed, converged)
    m.send_msg((host, 2001), mesg.pack(), False)

def create_sendlist(node_list, dv):
    sendlist = []
    for i in range(5):
        if dv[i] != 999 and dv[i] != 0:
            sendlist.append(node_list[i] + (dv[i],))
    return sendlist

def calc_distance(distances, dv, sendlist, port):
    for i in range(5):
        if i != port - 2000:
            tmp  = []
            for n in sendlist:
                cost = n[2] + int(distances[i])
                tmp.append(cost if cost < dv[i] else dv[i])
            dv[i] = min(tmp)
    return dv

def create_dvmatrix(file):
    current_node = 0
    lines = file.readlines()
    dv = []
    for line in lines:
        array = []
        line = line.rstrip()
        line = line.split()
        for i in range(len(line)):
            if line[i] != '0':
                array.append(int(line[i]))
            else:
                array.append(999 if current_node != i else 0)    
        dv.append(array)
        current_node += 1
    return dv

def print_update(node_id, dv, prev_node_id, distances, sendlist, port, old_dv, output_file):
    print(f"Node {node_id} received DV from {prev_node_id}")
    print(f"Updating DV matrix at node {node_id}")
    new_dv = calc_distance(distances, dv, sendlist, port)
    print(f"New DV matrx at node {node_id} = {new_dv}\n")
    output_file.write(f"Node {node_id} received DV from {prev_node_id}\n")
    output_file.write(f"Updating DV matrix at node {node_id}\n")
    output_file.write(f"New DV matrx at node {node_id} = {new_dv}\n\n")
    return 'false' if old_dv == dv else 'true'
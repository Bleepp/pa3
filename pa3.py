import threading
import concurrent.futures
import node as n


if __name__ == "__main__":
    lock = threading.Lock()
    file = open('network.txt', 'r')
    output_file = open('output.txt', 'a')
    dv = n.create_dvmatrix(file)
    dvmatrix = dv
    node_list = [('A', 2000), ('B', 2001), ('C', 2002), ('D', 2003), ('E', 2004)]
    barrier = threading.Barrier(5)
    with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
        executor.submit(n.node, ('A', 2000, barrier, True , dv[0], node_list, lock, output_file))
        executor.submit(n.node, ('B', 2001, barrier, False, dv[1], node_list, lock, output_file))
        executor.submit(n.node, ('C', 2002, barrier, False, dv[2], node_list, lock, output_file))
        executor.submit(n.node, ('D', 2003, barrier, False, dv[3], node_list, lock, output_file))
        executor.submit(n.node, ('E', 2004, barrier, False, dv[4], node_list, lock, output_file))
    
    file.close()
    output_file.close()

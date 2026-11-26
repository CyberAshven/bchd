# TEST ONLY: a TCP relay that forwards the first connection it takes to the
# target and holds every later one open without a byte, like a node that
# answers one call and then stalls.
import socket
import sys
import threading

listen_port, target_port = int(sys.argv[1]), int(sys.argv[2])
srv = socket.create_server(("127.0.0.1", listen_port))
held = []


def pipe(a, b):
    try:
        while True:
            data = a.recv(65536)
            if not data:
                break
            b.sendall(data)
    except OSError:
        pass
    finally:
        for s in (a, b):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


count = 0
while True:
    conn, _ = srv.accept()
    count += 1
    if count == 1:
        up = socket.create_connection(("127.0.0.1", target_port))
        threading.Thread(target=pipe, args=(conn, up), daemon=True).start()
        threading.Thread(target=pipe, args=(up, conn), daemon=True).start()
        print("relay: forwarded connection 1", flush=True)
    else:
        held.append(conn)
        print("relay: holding connection %d" % count, flush=True)

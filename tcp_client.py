import socket

def run_tcp_client(server_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, 54321))
    
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(data.decode().strip())
    client_socket.close()

if __name__ == "__main__":
    run_tcp_client("127.0.0.1")

import socket
import threading

clients = {}  # Store each player's socket by ID

# Function to handle each client's connection
def handle_client(client_socket, player_id):
    print(f"Player {player_id} connected.")
    # Placeholder message to interact with the client (to be expanded later)
    client_socket.send(f"Welcome Player {player_id}".encode())

    # Wait for the client to send a message (can be used for picking a box in the game)
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break  # Connection was closed
            print(f"Received from Player {player_id}: {data.decode()}")
            message = f"{player_id}:{data.decode()}"  # Format: "1:0,2"
            print(f"Broadcasting to all: {message}")

            for pid, sock in clients.items():
                try:
                    sock.sendall(message.encode())
                except:
                    print(f"Failed to send to Player {pid}")

        except ConnectionResetError:
            break  # Handle case where client disconnects abruptly
    client_socket.close()
    print(f"Player {player_id} disconnected.")

# Main function to start the server
def run_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 54321))  # Bind to port 53333
    server_socket.listen(5)  # Can handle up to 5 clients at a time
    print("TCP Server listening on port 53333...")

    player_id = 1  # Starting player ID
    while True:
        # Accept a new connection from a player
        client_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")

        # Start a new thread for the new player
        threading.Thread(target=handle_client, args=(client_socket, player_id)).start()
        clients[player_id] = client_socket

        # Increment player ID for the next player
        player_id += 1

if __name__ == "__main__":
    run_tcp_server()
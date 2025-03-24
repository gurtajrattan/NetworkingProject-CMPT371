import socket
import threading
import random 

#global dictionary to store players: key = playerID, value = client socket
players = {}

clients = {}  # Store each player's socket by ID

itPlayerID = None

# Function to handle each client's connection
def handle_client(client_socket, player_id):
    print(f"Player {player_id} connected.")
    # Placeholder message to interact with the client (to be expanded later)
    #client_socket.send(f"Welcome Player {player_id}".encode())
    # Send a waiting message if fewer than 2 players are connected
    if len(players) < 3:
        client_socket.send("Waiting for players to connect...".encode())
    
    # When exactly 2 players are connected, start the game
    if len(players) == 3:
        global itPlayerID 
        itPlayerID = assign_it()
        start_game(itPlayerID)
    


    # Wait for the client to send a message (can be used for picking a box in the game)
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break  # Connection was closed
            decoded = data.decode()
            print(f"Received from Player {player_id}: {decoded}")
            message = f"{player_id}:{decoded}"  # Format: "1:0,2"

# If sender is IT, log the message and do not broadcast it.
            if player_id == itPlayerID:
                #print(f"Not broadcasting IT's selection: {decoded}")
                continue
            else:
                # Broadcast to all connected clients
               for pid, sock in clients.items():
                    try:
                        # Skip sending the selection to the IT client
                        if pid == itPlayerID:
                            print(f"Not broadcasting IT's selection: {decoded}")
                            continue
                        sock.sendall(message.encode())
                    except Exception as e:
                        print(f"Failed to send to Player {pid}: {e}")
                        
        except ConnectionResetError:
            break  # Handle disconnection

    client_socket.close()
    print(f"Player {player_id} disconnected.")

def assign_it():
    it_player = random.choice(list(players.keys()))
    print(f"Player {it_player} is assigned as IT.")
    return it_player

def start_game(it_player):
    for pid, sock in players.items():
        startMsg = f"Game starting! IT: {it_player}; YourID: {pid}"
        sock.send(startMsg.encode())

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

        players[player_id] = client_socket
        clients[player_id] = client_socket

        print(f"Player {player_id} added. Total players: {len(players)}")
        
        # Start a new thread for the new player
        threading.Thread(target=handle_client, args=(client_socket, player_id)).start()

        # Increment player ID for the next player
        player_id += 1

if __name__ == "__main__":
    run_tcp_server()
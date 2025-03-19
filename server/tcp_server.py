import socket
import threading
import random

# Function to handle each client's connection
def handle_client(client_socket, player_id, players):
    print(f"Player {player_id} connected.")
    
    # Send a waiting message if fewer than 4 players are connected
    if len(players) < 4:
        client_socket.send(f"Welcome Player {player_id}! Waiting for other players...".encode())
    
    # Once all 4 players are connected, start the game
    if len(players) == 4:
        assign_it(players)  # Assign IT
        start_game(players)  # Notify all players that the game has started

    # Wait for the client to send a message (this will be expanded to select boxes later)
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break  # Connection was closed
            print(f"Received from Player {player_id}: {data.decode()}")
            client_socket.send(f"Player {player_id}, you sent: {data.decode()}".encode())
        except ConnectionResetError:
            break  # Handle case where client disconnects abruptly
    client_socket.close()
    print(f"Player {player_id} disconnected.")

# Function to assign a random player as IT
def assign_it(players):
    if len(players) == 4:  # Only assign IT when there are exactly 4 players
        it_player = random.choice(list(players.keys()))  # Pick a random player
        players['it'] = it_player
        print(f"Player {it_player} is assigned as IT.")
        return it_player
    return None

# Function to notify all players that the game is starting
def start_game(players):
    it_player = players['it']
    for player_id, client_socket in players.items():
        if player_id != 'it':  # Skip the 'it' key
            client_socket.send(f"Game starting! Player {it_player} is IT.".encode())
        else:
            client_socket.send(f"Game starting! You are Player {it_player}, and you are IT.".encode())

# Main function to start the server
def run_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 53333))  # Bind to port 53333
    server_socket.listen(5)  # Can handle up to 5 clients at a time
    print("TCP Server listening on port 53333...")

    players = {}  # Store player info {player_id: client_socket}
    player_id = 1  # Starting player ID

    while True:
        # Accept a new connection from a player
        client_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")

        # Add player to the list
        players[player_id] = client_socket
        print(f"Player {player_id} added.")

        # Start a new thread for the new player
        threading.Thread(target=handle_client, args=(client_socket, player_id, players)).start()

        # Increment player ID for the next player
        player_id += 1

if __name__ == "__main__":
    run_tcp_server()

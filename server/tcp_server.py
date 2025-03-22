import socket
import threading
import random 

#global dictionary to store players: key = playerID, value = client socket
players = {}

# Function to handle each client's connection
def handle_client(client_socket, player_id):
    print(f"Player {player_id} connected.")
    # Placeholder message to interact with the client (to be expanded later)
    #client_socket.send(f"Welcome Player {player_id}".encode())
    # Send a waiting message if fewer than 2 players are connected
    if len(players) < 2:
        client_socket.send("Waiting for players to connect...".encode())
    
    # When exactly 2 players are connected, start the game
    if len(players) == 2:
        it_player = assign_it()  # Assign IT among the two
        start_game(it_player)
    

    # Wait for the client to send a message (can be used for picking a box in the game)
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


def assign_it():
    it_player = random.choice(list(players.keys()))
    print(f"Player {it_player} is assigned as IT.")
    return it_player

def start_game(it_player):
    start_message = f"Game starting! Player {it_player} is IT."
    for pid, sock in players.items():
        sock.send(start_message.encode())

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
        print(f"Player {player_id} added. Total players: {len(players)}")
        
        # Start a new thread for the new player
        threading.Thread(target=handle_client, args=(client_socket, player_id)).start()

        # Increment player ID for the next player
        player_id += 1

if __name__ == "__main__":
    run_tcp_server()
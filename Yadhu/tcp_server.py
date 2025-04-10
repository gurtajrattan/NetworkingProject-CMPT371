import socket
import threading
from gameLogic import gameLogic
import time

GRID_SIZE = 3
clients = {}         # {player_id: client_socket}
clients_lock = threading.Lock()
game_logic = gameLogic(GRID_SIZE)
max_players = 4      # Supports 4 players

""" Function to send message to all connected players via TCP """
def broadcast_to_all(message):
    # Send a message to all connected clients.
    with clients_lock:
        for pid, sock in clients.items():
            try:
                sock.sendall((message + "\n").encode())
            except Exception as e:
                print(f"Failed to send message to Player {pid}: {e}")


""" 
    Function to parse messages from an incoming player
    The function parses all incoming messages, 
    If the message is the external box, the server will update all players regarding message.
    The server will update its verison of the game logic, and when a player is immune, the server 
    will broadcast it to all players and stop any new clicks.
    If the message is not the external box, the server will process it as selecting a square.
    The server will then use the game logic and communicate with the player on its selection. 
    Last of all it will then send the current state of the board to all players.
    If the player disconnects, the server will remove the player from connected clients.
"""
def handle_client(client_socket, player_id):
    # Handle incoming messages from a client.
    print(f"Player {player_id} connected.")
    try:
        welcome = f"Welcome Player {player_id}"
        client_socket.sendall((welcome + "\n").encode())
        client_socket.sendall((game_logic.get_serialized_grid(revealIT=False) + "\n").encode())
    except Exception as e:
        print("Error sending initial message to Player", player_id, e)

    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        message = data.decode().strip()
        print(f"Received from Player {player_id}: {message}")
        if message == "external":
            success, response = game_logic.recordExternalClick(player_id)
            client_socket.sendall(("msg:" + response + "\n").encode())
            # Optionally, broadcast the current external box state:
            broadcast_to_all(game_logic.get_serialized_external_box())
            continue
        # Otherwise, assume grid click and process as usual:
        try:
            row, col = map(int, message.split(","))
        except:
            client_socket.sendall("msg:Invalid selection format.\n".encode())
            continue
        success, response = game_logic.recordSelection(player_id, row, col)
        client_socket.sendall(("msg:" + response + "\n").encode())
        
        if success:
            broadcast_to_all(game_logic.get_serialized_grid(revealIT=False))
            
    client_socket.close()
    print(f"Player {player_id} disconnected.")
    with clients_lock:
        if player_id in clients:
            del clients[player_id]

""" 
    Function handles the game loop on server side.
    When round is complete server then updates all players of the round's results.
    It then calculates if someone has been tagged 3 times, if true, the server then tells all players
    who loses, and disconnects all players and exits.
    Otherwise continue with game and send players new board and who is IT.
"""
def game_manager():
    # Main loop for processing rounds and broadcasting results.
    while True:
        game_logic.round_complete.wait()
        result = game_logic.processRound()
        broadcast_to_all(game_logic.get_serialized_grid(revealIT=True))
        broadcast_to_all("msg:" + result)
        loser = game_logic.gameOver()
        if loser is not None:
            broadcast_to_all(f"msg:Game over! Player {loser} reached 3 tags and loses the game.")

            # Wait a bit so all clients can read the message.
            
            time.sleep(8)

            # Close all client sockets when game ends.
            with clients_lock:
                for pid, sock in clients.items():
                    try:
                        sock.close()
                    except:
                        pass

            break

        game_logic.newRound()
        broadcast_to_all(game_logic.get_serialized_grid(revealIT=False))
        broadcast_to_all(f"msg:New round started. IT is Player {game_logic.it_player}")
        broadcast_to_all(f"IT {game_logic.it_player}")

""" 
    TCP server on port 54321, Server assigns player_id to players based on order of connection.
    Creates a separate thread for each player, which parses incoming messages and updates server of game state.
    When the amount of players joined reaches the max_players, the server intializes the game.
    The server then tells all clients, which player is IT and starts the game.
    Once game is over, the server will shutdown.
"""
def run_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 54321))
    server_socket.listen(5)
    print("TCP Server listening on port 54321...")
    player_id = 1
    while player_id <= max_players:
        client_socket, addr = server_socket.accept()
        print(f"New connection from {addr}")
        with clients_lock:
            clients[player_id] = client_socket
        threading.Thread(target=handle_client, args=(client_socket, player_id), daemon=True).start()
        player_id += 1
    game_logic.initializeGame(list(range(1, max_players + 1)))
    broadcast_to_all(f"msg:Game started! Initial IT is Player {game_logic.it_player}, REMEMBER the IT cannot go until all players have selected a sqaure!")
    broadcast_to_all(f"IT {game_logic.it_player}")
    game_manager_thread = threading.Thread(target=game_manager, daemon=True)
    game_manager_thread.start()
    game_manager_thread.join()
    server_socket.close()

if __name__ == "__main__":
    run_tcp_server()

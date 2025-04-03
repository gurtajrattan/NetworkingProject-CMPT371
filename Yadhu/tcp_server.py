import socket
import threading
from gameLogic import gameLogic
import time

GRID_SIZE = 3
clients = {}         # {player_id: client_socket}
clients_lock = threading.Lock()
game_logic = gameLogic(GRID_SIZE)
max_players = 4      # Supports 4 players

def broadcast_to_all(message):
    #Send a message to all connected clients.
    with clients_lock:
        for pid, sock in clients.items():
            try:
                sock.sendall((message + "\n").encode())
            except Exception as e:
                print(f"Failed to send message to Player {pid}: {e}")

def handle_client(client_socket, player_id):
    #Handle incoming messages from a client.
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

def game_manager():
    #Main loop for processing rounds and broadcasting results.
    while True:
        game_logic.round_complete.wait()
        result = game_logic.processRound()
        broadcast_to_all(game_logic.get_serialized_grid(revealIT=True))
        broadcast_to_all("msg:" + result)
        loser = game_logic.gameOver()
        if loser is not None:
            broadcast_to_all(f"msg:Game over! Player {loser} reached 5 tags and loses the game.")

            # Wait a bit so all clients can read the message
            
            time.sleep(8)

            # close all client sockets
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
    game_manager_thread = threading.Thread(target=game_manager, daemon=True)
    game_manager_thread.start()
    game_manager_thread.join()
    server_socket.close()

if __name__ == "__main__":
    run_tcp_server()

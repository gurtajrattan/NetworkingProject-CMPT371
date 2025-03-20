import socket
import time

# Function to run the TCP client and connect to the server
def run_tcp_client(server_ip):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, 5321))
    
    # Receive the initial welcome message and current IT player info
    welcome_message = client_socket.recv(1024).decode()
    print(welcome_message)  # Print the welcome message from the server

    # Wait for all 4 players to join the game
    while "Waiting for the game to start" in welcome_message:
        welcome_message = client_socket.recv(1024).decode()
        print(welcome_message)  # Continue to print messages from server

    # Once the game starts, display IT player info
    if "IT" in welcome_message:
        print(f"Game started! {welcome_message}")
    
    # Additional game logic to handle player actions can go here.
    # For now, the client will just display the IT player info and close the connection.
    
    # Close the connection
    client_socket.close()

if __name__ == "__main__":
    # Replace 'server_ip' with the actual IP address of your server if not localhost
    run_tcp_client("127.0.0.1")

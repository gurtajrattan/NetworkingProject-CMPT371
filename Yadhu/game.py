import pygame
import socket
import select
from gameLogic import gameLogic

pygame.init()
GRID_SIZE = 3
CELL_SIZE = 100
WINDOW_SIZE = (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Waiting for players....")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)    # Blue
YELLOW = (255, 255, 0)  # Yellow
MAGENTA = (255, 0, 255)   # Magenta, 
RED = (255, 0, 0)

is_IT = False #true if client is IT
myPlayerID = None
playerID = None  # This will store the player's ID
IT_id = None

playerColors = {
    1: GREEN,
    2: BLUE,
    3: YELLOW,
    4: MAGENTA
}

IT_color = RED

#gamelogic is class from gameLogic, makes an instance
game_logic = gameLogic()
has_selected_box = False  # Track if the player already clicked

#connect to the server
#create new socket, w IPv4, TCP
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connect to port
clientSocket.connect(('127.0.0.1', 54321))

response = clientSocket.recv(1024).decode()
print("Server's response: ", response)

# The response contains the player ID
if "Welcome Player" in response:
    playerID = int(response.split(" ")[2])  # Extract the player ID

def drawGrid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            val = game_logic.grid[row][col]
            # Fill the cell: if empty, use white; if filled, use GREEN or RED.
            if val != '':
                if "IT" in val:
                    pygame.draw.rect(window, RED, rect)
                else:
                    pygame.draw.rect(window, playerColors[playerID], rect)
            else:
                pygame.draw.rect(window, BLACK, rect)
            # Draw the border for the cell
            pygame.draw.rect(window, WHITE, rect, 1)

def parse_grid_message(message):
    # Expected format: "grid:cell,cell,cell|cell,cell,cell|cell,cell,cell"
    grid_data = message[len("grid:"):]
    rows = grid_data.split("|")
    new_grid = []
    for row_str in rows:
        cells = row_str.split(",")
        new_grid.append([cell.strip() for cell in cells])
    return new_grid

def process_server_message(message):
    if message.startswith("grid:"):
        new_grid = parse_grid_message(message)
        game_logic.grid = new_grid
    elif message.startswith("msg:"):
        info = message[len("msg:"):]
        print(info)
        # If a new round has started, allow a new selection.
        if "New round started" in info:
            global has_selected_box
            has_selected_box = False
    else:
        print("Server:", message)

clock = pygame.time.Clock()
running = True
while running:
    # Fill the background with white instead of black.
    window.fill(WHITE)
    drawGrid()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not has_selected_box:
                x, y = event.pos
                row, col = y // CELL_SIZE, x // CELL_SIZE
                selection = f"{row},{col}"
                clientSocket.sendall((selection + "\n").encode())
                print("Sent selection:", selection)
                has_selected_box = True
    
    # Process messages from the server
    readable, _, _ = select.select([clientSocket], [], [], 0)
    for sock in readable:
        try:
            data = sock.recv(1024).decode()
            if data:
                messages = data.split("\n")
                for msg in messages:
                    if msg.strip() != "":
                        process_server_message(msg.strip())
        except Exception as e:
            print("Error receiving data:", e)
    
    pygame.display.update()
    clock.tick(30)

clientSocket.close()
pygame.quit()

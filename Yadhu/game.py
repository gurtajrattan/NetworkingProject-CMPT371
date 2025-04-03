import pygame
import socket
import select
from gameLogic import gameLogic

pygame.init()
GRID_SIZE = 3
CELL_SIZE = 100
WINDOW_SIZE = (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("TAG")
# Add this near your existing window setup:
EXTERNAL_BOX_HEIGHT = 100  # extra space for the external immunity box
WINDOW_SIZE = (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE + EXTERNAL_BOX_HEIGHT)
window = pygame.display.set_mode(WINDOW_SIZE)
my_player_id = None

external_clicks = {}       # Dictionary to hold {player_id: click_count}
external_box_locked = False  # Flag to indicate if the box is locked

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# This instance is used only to store the grid state received from the server.
game_logic = gameLogic(GRID_SIZE)
has_selected_box = False

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect(('127.0.0.1', 54321))

def drawGrid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            cell_val = game_logic.grid[row][col]
            # Fill the cell: if empty, use white; if filled, use GREEN or RED.
            if cell_val != '':
                if "IT" in cell_val:
                    pygame.draw.rect(window, RED, rect)
                else:
                    pygame.draw.rect(window, GREEN, rect)
            else:
                pygame.draw.rect(window, WHITE, rect)
            # Draw the border for the cell
            pygame.draw.rect(window, BLACK, rect, 1)

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
    global has_selected_box, running, my_player_id, external_clicks, external_box_status
    if message.startswith("Welcome Player"):
        try:
            my_player_id = int(message.split()[-1])
            print(f"Assigned player ID: {my_player_id}")
        except Exception as e:
            print("Error parsing player ID:", e)
    elif message.startswith("grid:"):
        new_grid = parse_grid_message(message)
        game_logic.grid = new_grid
    elif message.startswith("external:"):
        data = message[len("external:"):]
        if data == "acquired":
            external_box_status = "acquired"
            external_clicks = {}
            print("Immunity has been acquired for this round.")
        else:
            external_box_status = "active"
            external_clicks = {}
            for item in data.split(","):
                if item:
                    pid, count = item.split(":")
                    external_clicks[int(pid)] = int(count)
            print("External box state updated:", external_clicks)
    elif message.startswith("msg:"):
        info = message[len("msg:"):]
        print(info)
        if "Selection recorded" in info:
            has_selected_box = True
        elif "New round started" in info:
            has_selected_box = False
            # Reset external box status each round:
            external_box_status = "active"
            external_clicks = {}
        elif "Game over!" in info:
            print("Game over! Closing client.")
            running = False
    else:
        print("Server:", message)


def drawExternalBox():
    # Only non‑IT players see the external box and only if it's not locked.
    if my_player_id is not None and my_player_id != game_logic.it_player and not external_box_locked:
        rect = (10, GRID_SIZE * CELL_SIZE + 10, CELL_SIZE, EXTERNAL_BOX_HEIGHT - 20)
        pygame.draw.rect(window, GREEN, rect)
        font = pygame.font.Font(None, 36)
        count = external_clicks.get(my_player_id, 0)
        text = font.render(f"{count}/7", True, WHITE)
        window.blit(text, (rect[0] + 5, rect[1] + (rect[3] // 2 - 18)))

clock = pygame.time.Clock()
running = True
while running:
    # Fill the background with white instead of black.
    window.fill(WHITE)
    drawGrid()
    drawExternalBox()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Click in the external box area:
            if y >= GRID_SIZE * CELL_SIZE:
                if my_player_id is not None and my_player_id != game_logic.it_player:
                    if external_box_locked:
                        print("External box is locked; no further clicks allowed.")
                    else:
                        clientSocket.sendall(("external\n").encode())
                        print("External box clicked")
                else:
                    print("IT cannot click the external box.")
            elif not has_selected_box:
                row, col = y // CELL_SIZE, x // CELL_SIZE
                selection = f"{row},{col}"
                clientSocket.sendall((selection + "\n").encode())
                print("Sent selection:", selection)
    
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

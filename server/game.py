import pygame
import socket
from gameLogic import gameLogic
import select
##THIS FILE HANDLES THE FRONTEND OF THE GAME, TO CREATE GAME WINDOW
##INCLUDES VISUAL ELEMENTS AND TRANSLATE USER INPUTS LIKE MOUSE CLICKS
##TO ACTIONS, GAME.PY CAPTURES COORDINATES AND CALLS GAMELOGIC BASED ON THE INPUTS


#initialize pygame
pygame.init()

#define constants for grid
GRID_SIZE = 3 # 3x3
CELL_SIZE = 100 #100 pixels
WINDOW_SIZE = (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE) #sets size of window to display grid
window = pygame.display.set_mode(WINDOW_SIZE) #makes the pygame window

pygame.display.set_caption("Waiting for players....") 

#colors
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
if "Your player ID is" in response:
    playerID = int(response.split(" ")[4])  # Extract the player ID



def drawGrid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(window, WHITE, rect, 1)  # Draw border

            val = game_logic.grid[row][col]

            if val != '':
                if is_IT:
                    # IT sees only their own selection
                    if val == myPlayerID:
                        pygame.draw.rect(window, IT_color, rect)
                else:
                    # Non-IT: show all players' selections (including own)
                    if val == myPlayerID:
                        
                        pygame.draw.rect(window, playerColors[playerID], rect)
                    elif val in playerColors:
                        pygame.draw.rect(window, playerColors[val], rect)


           


def playerSelectionHandler(row, col):
    global has_selected_box

    if has_selected_box:
        print("You already selected a box!")
        return

    if is_IT:
        if not game_logic.itSelectBox(row, col):
            return
        selection_message = f"IT:{row},{col}"
        game_logic.grid[row][col] = myPlayerID  # <== IMMEDIATE LOCAL UPDATE
    else:
        if not game_logic.playerSelectBox(myPlayerID, row, col):
            print("Selection invalid. Box already taken.")
            return
        selection_message = f"{row},{col}"
        game_logic.grid[row][col] = myPlayerID  # <== IMMEDIATE LOCAL UPDATE

    try:
        clientSocket.sendall(selection_message.encode())
        print(f"Sent selection to server: {selection_message}")
    except Exception as e:
        print("Error sending selection:", e)

    has_selected_box = True



loop = True
while loop:
    #clear screen
    window.fill(BLACK) 
    #draw the grid
    drawGrid()

    #listen for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
        
        # if mouse click, translate coordinates
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            #This divides the y coordinate of the mouse click by CELL_SIZE.
            #ives you the row index of the grid where the click happened.
            row, col = y //CELL_SIZE, x //CELL_SIZE
            print(f"Selected box () ({row}, {col})")
            playerSelectionHandler(row, col)

    readable, _, _ = select.select([clientSocket], [], [], 0)
    for sock in readable:
        try:
            data = sock.recv(1024).decode()
            if data:
                
                # If the response is a waiting message, display it on the window and wait for the game to start.
                if "Waiting for players" in data:
                    pygame.display.set_caption("Waiting for players...")

                # You can add a loop here to wait for a "Game starting" message before proceeding:
                if playerID < 3:
                    while "Waiting" in data:
                        print("Server's response: ", data)
                        data = clientSocket.recv(1024).decode()
                        # Optionally, update the window or a text overlay in Pygame to inform the user
                        if "Game starting" in data or "IT" in data:
                            pygame.display.set_caption(f"YourID: {str(playerID)}, IT's id: {str(IT_id)}")
                            break
                else:
                    pygame.display.set_caption(f"YourID: {str(playerID)}")
                    
                print("Received update:", data)

                parts = data.split(":")
                if len(parts) >= 2:
                    pid = int(parts[0])
                    coords = parts[1]
                    row, col = map(int, coords.split(","))
                    # If this client is IT, only update the cell if the update is from IT itself.
                if is_IT:
                    if pid == myPlayerID:
                        game_logic.grid[row][col] = pid
                    else:
                        # Ignore updates from other players on IT's client.
                        continue
                else:
                    # For non-IT clients, update only if the cell is empty.
                    if game_logic.grid[row][col] == '':
                        game_logic.grid[row][col] = pid
        except Exception as e:
            print("Error receiving update:", e)

    pygame.display.update() #update the display 

# Close the socket when done
clientSocket.close()  
pygame.quit()  

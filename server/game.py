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

pygame.display.set_caption("TAG") 

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
GREEN = (0, 255, 0)


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

#function to draw grid
def drawGrid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            pygame.draw.rect(window, WHITE, rect, 1)  # Draw border

            val = game_logic.grid[row][col]
            if val == 'locked':  #  This is the key line
                pygame.draw.rect(window, GREEN, rect)
            elif val == 'X':
                pygame.draw.rect(window, GRAY, rect)
            elif val == 'O':
                pygame.draw.rect(window, BLACK, rect)



#function for when player clicks on a box
def playerSelectionHandler(row, col):
    global has_selected_box

    if has_selected_box:
        print("You already selected a box!")
        return

    if game_logic.grid[row][col] == 'locked':
        print("Box already taken.")
        return

    # Send coordinates to the server
    selection = f"{row},{col}"
    clientSocket.sendall(selection.encode())
    print(f"Sent selection to server: {selection}")

    has_selected_box = True  #  Mark that this player has moved





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
                print("Received update:", data)
                player_id, coords = data.split(":")
                row, col = map(int, coords.split(","))
                game_logic.grid[row][col] = 'locked'
        except Exception as e:
            print("Error receiving update:", e)

    pygame.display.update() #update the display 

# Close the socket when done
clientSocket.close()  
pygame.quit()  




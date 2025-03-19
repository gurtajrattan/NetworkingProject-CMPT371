import pygame
import socket
from gameLogic import GameLogic
import bo
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

#gamelogic is class from gameLogic, makes an instance
game_logic = GameLogic()

#connect to the server
#create new socket, w IPv4, TCP
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connect to port
clientSocket.connect(('localhost', 53333))


#function to draw grid
def drawGrid():
    for row in range (GRID_SIZE):
        for col in range (GRID_SIZE):
            #draw box at (r,c) 
            pygame.draw.rect(window, WHITE,  (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
 
            #fill boxes 
            #keep track of each box's state
            if game_logic.grid[row][col] == 'X': #selected boxed
                pygame.draw.rect(window, GRAY, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            elif game_logic.grid[row][col] == 'O': #IT's selection
                pygame.draw.rect((window, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1))


#function for when player clicks on a box
def playerSelectionHandler(row, col):
    #send the coordinates to server
    selection = f"{row},{col}"
    clientSocket.sendall(selection.encode())

    #wait for server's response 
    response = clientSocket.recv(1024).decode()
    print("Server's response: ", response)


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

    pygame.display.update() #update the display 

# Close the socket when done
clientSocket.close()  
pygame.quit()  




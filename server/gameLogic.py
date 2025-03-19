import random

class gameLogic:
    #initialize var of class 
    def __init__(self, gridSize=3):
        self.gridSize = gridSize;
        self.grid = []
        for i in range(gridSize):
            row = []
            for j in range(gridSize):
                row.append('')
            self.grid.append(row)

        self.players = []  # List of players (could be player IDs)
        self.it_player = None  # Player who is "IT"
        self.it_count = {}  # Count of how many times each player has been IT
        self.boxSelected = {}
        self.game_over = False  # Flag to track if the game is over

    def initializeGame(self, playerIDs):
        #initialize with players id
        self.players = playerIDs
        self.it_count = {}
        for playerID in playerIDs:
            #set IT count to 0 for each player ID
            self.it_count[playerID] = 0; 

        self.assignIT(firstRound=True)
    
    def assignIT(self, taggedPlayer=None, firstRound=False):
        #randomly assign IT in first round
        if firstRound:
            self.it_player = random.choice(self.players)
            print(f"First Round: player {self.it_player} is now IT.")
        
        else:
            #for other rounds check if another player has been tagged
            taggedPlayer = self.checkTagged()

            if taggedPlayer: 
                #someone has been tagged update IT player
                self.it_player=taggedPlayer
                numOfIT = self.updateCount(self, self.it_player)
                print(f"Player {self.it_player} is now IT and has been tagged {numOfIT} times.")
            else: 
                #no one is tagged, taggedplayer is None (returned from checkTagged)
                numOFIT = self.updateCount(self, self.it_player)
                print(f"Player {self.it_player} is now IT and has been tagged {numOfIT} times.")
            
            self.resetGrid()


    def playerSelectBox(self, playerID, row, col):
        #check if box is alr taken taken
        if (row, col) in self.boxSelected.values():
            print(f"Box at ({row}, {col}) is already selected. Try again.")
            return False
        
        #otherwise player can have box
        self.boxSelected[playerID] = (row, col)
        self.grid[row][col] = playerID
        return True
    
    def itSelectBox(self, row, col):
        #IT Players selection
        #can choose any box;
        self.grid[row][col] = self.it_player
        print(f"IT player {self.it_player} has selected box ({row}, {col}).")
        return True

    
    def displayITBox(self):
        #reveal the box selected
        print(f"IT's box is revealed: Player {self.it_player} selected a box.")
        #display coordinates 

    def checkTagged(self):
        #checks if box at r,c in the grid is same as player
        for playerID, (row, col) in self.boxSelected.items():
            if self.grid[row][col] == self.it_player:
                print(f"Player {playerID} is tagged and becomes IT!")
                return playerID  # The tagged player becomes the new I
        return None 
        
    
    #update IT count
    def updateCount(self, playerID):
        self.it_count[playerID]+=1
        return self.it_count[playerID]
    

    def gameOver(self, playerID):
        if self.it_count[playerID] >= 3:
            self.game_over = True
            print(f"Player {playerID} has been IT 3 times and loses the game!")
            return True
        return False
    
    def resetGrid(self):
        self.grid = []
        for i in range(self.gridSize):
            row = []
            for j in range(self.gridSize):
                row.append('')
            self.grid.append(row)


    def handleRound(self):
        #handles the round in the game
        print("Players are selecting boxes...")
        # Here you would simulate player selections (e.g., using input from the UI)
        # For this example, assume players make their selections (mocked)
    
    def end_game(self):
        print(f"Game over! Player {self.it_player} has lost the game!")
        # Optionally, reset the game or announce the winner here

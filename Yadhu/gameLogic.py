import random
import threading

class gameLogic:
    def __init__(self, gridSize=3):
        self.gridSize = gridSize
        self.players = []             # List of player IDs (integers)
        self.it_player = None         # Current IT player's ID
        self.it_count = {}            # Count of times each player has been IT
        self.selections = {}          # For non‑IT players: {player_id: (row, col)}
        self.it_selection = None      # IT player's selection: (row, col)
        self.grid = [['' for _ in range(gridSize)] for _ in range(gridSize)]
        self.lock = threading.Lock()
        self.round_complete = threading.Event()  # Signals that all selections have been made

    def initializeGame(self, playerIDs):
        # Initialize players, set IT counts, and randomly choose the first IT.
        self.players = playerIDs
        for pid in playerIDs:
            self.it_count[pid] = 0
        self.it_player = random.choice(playerIDs)
        print(f"Initial IT: Player {self.it_player}")
        self.newRound()

    def newRound(self):
        # Reset grid and selections for a new round.
        with self.lock:
            self.grid = [['' for _ in range(self.gridSize)] for _ in range(self.gridSize)]
            self.selections = {}
            self.it_selection = None
            self.round_complete.clear()
            print("New round started. Waiting for selections...")

            self.immunity_clicks = {}   # {player_id: click_count}
            self.immunity_awarded = None  # player_id who earned immunity this round
    
    def recordExternalClick(self, player_id):
        with self.lock:
            # Do not allow any more clicks if immunity is already awarded.
            if self.immunity_awarded is not None:
                return False, "External box is locked. Immunity already acquired for this round."
            if player_id not in self.immunity_clicks:
                self.immunity_clicks[player_id] = 0
            self.immunity_clicks[player_id] += 1
            count = self.immunity_clicks[player_id]
            if count >= 7:
                if player_id != self.it_player:
                    self.immunity_awarded = player_id
                    print(f"Player {player_id} acquired immunity for this round!")  # Server terminal print
                    return True, f"Player {player_id} earned immunity for this round!"
                else:
                    return False, "IT cannot earn immunity."
            return True, f"Player {player_id} external click recorded ({count}/7)."


    def get_serialized_external_box(self):
        with self.lock:
            if self.immunity_awarded is not None:
                return "external:acquired"
            parts = []
            for pid, count in self.immunity_clicks.items():
                parts.append(f"{pid}:{count}")
            return "external:" + ",".join(parts)


    def recordSelection(self, player_id, row, col):
        with self.lock:
            if row < 0 or row >= self.gridSize or col < 0 or col >= self.gridSize:
                return False, "Invalid cell."

            # Delay IT until all other players have selected.
            if player_id == self.it_player:
                if len(self.selections) < (len(self.players) - 1):
                    return False, "Please wait for all players to select before making your move."
                if self.it_selection is not None:
                    return False, "You have already selected a box."
                self.it_selection = (row, col)
                self.grid[row][col] = "IT"
                print(f"IT (Player {player_id}) selected box at ({row}, {col}).")
            else:
                if player_id in self.selections:
                    return False, "You have already selected a box."
                if (row, col) in self.selections.values():
                    return False, "Another player already selected that box. Pick a different one."
                self.selections[player_id] = (row, col)
                self.grid[row][col] = str(player_id)
                print(f"Player {player_id} selected box at ({row}, {col}).")

            if self.it_selection is not None and len(self.selections) == (len(self.players) - 1):
                self.round_complete.set()

            return True, "Selection recorded."



    def processRound(self):
        
        """ Once all selections have been received, reveal IT's selection and check if any non‑IT
        player picked the same box. Update IT count and assign new IT if needed. """
        self.round_complete.wait()
        with self.lock:
            it_row, it_col = self.it_selection
            tagged = None
            for pid, sel in self.selections.items():
                if sel == self.it_selection:
                    tagged = pid
                    break
            if tagged is not None:
                # If the tagged player has immunity, ignore the tag.
                if self.immunity_awarded == tagged:
                    result = f"Player {tagged} was tagged but is immune. IT remains Player {self.it_player}."
                    self.grid[it_row][it_col] = f"IT({self.it_player})"
                else:
                    self.it_count[tagged] += 1
                    result = f"Player {tagged} was tagged and becomes IT! (Tag count: {self.it_count[tagged]})"
                    self.grid[it_row][it_col] = f"IT({tagged})"
                    self.it_player = tagged
            else:
                result = f"No one was tagged. Player {self.it_player} remains IT."
                self.grid[it_row][it_col] = f"IT({self.it_player})"
            print(result)
            return result
    
    # This is check it does to see if the game is over.
    def gameOver(self):
        # Check if any player has been IT a certain amount of times.
        with self.lock:
            for pid, count in self.it_count.items():
                # To change the number of times someone can be tagged you change this number. 
                if count >= 3:
                    return pid
            return None

    def get_serialized_grid(self, revealIT=False):
        
        """ Serialize the grid into a string.
        If revealIT is False, IT's cell remains hidden (sent as a blank).
        Format: "grid:cell,cell,cell|cell,cell,cell|cell,cell,cell" """
        
        with self.lock:
            rows = []
            for i in range(self.gridSize):
                cells = []
                for j in range(self.gridSize):
                    cell = self.grid[i][j]
                    if cell == "IT" and not revealIT:
                        cells.append(" ")
                    else:
                        cells.append(cell if cell != "" else " ")
                rows.append(",".join(cells))
            return "grid:" + "|".join(rows)

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
        #Initialize players, set IT counts, and randomly choose the first IT.
        self.players = playerIDs
        for pid in playerIDs:
            self.it_count[pid] = 0
        self.it_player = random.choice(playerIDs)
        print(f"Initial IT: Player {self.it_player}")
        self.newRound()

    def newRound(self):
        #Reset grid and selections for a new round.
        with self.lock:
            self.grid = [['' for _ in range(self.gridSize)] for _ in range(self.gridSize)]
            self.selections = {}
            self.it_selection = None
            self.round_complete.clear()
            print("New round started. Waiting for selections...")

    def recordSelection(self, player_id, row, col):
        """Record a player's selection.
        For the IT player, record only one (and mark the cell as hidden).
        For non‑IT players, ensure no two choose the same box. """
        with self.lock:
            if row < 0 or row >= self.gridSize or col < 0 or col >= self.gridSize:
                return False, "Invalid cell."
            
            if player_id == self.it_player:
                if self.it_selection is not None:
                    return False, "You have already selected a box."
                else:
                    self.it_selection = (row, col)
                    self.grid[row][col] = "IT"
                    print(f"IT (Player {player_id}) selected box at ({row}, {col}).")
            else:
                if player_id in self.selections:
                    return False, "You have already selected a box."
                if (row, col) in self.selections.values():
                    return False, "Another player already selected that box."
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
                self.it_count[tagged] += 1
                result = f"Player {tagged} was tagged and becomes IT! (Tag count: {self.it_count[tagged]})"
                self.grid[it_row][it_col] = f"IT({tagged})"
                self.it_player = tagged
            else:
                result = f"No one was tagged. Player {self.it_player} remains IT."
                self.grid[it_row][it_col] = f"IT({self.it_player})"
            print(result)
            return result

    def gameOver(self):
        """ Check if any player has been IT three times. """
        with self.lock:
            for pid, count in self.it_count.items():
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

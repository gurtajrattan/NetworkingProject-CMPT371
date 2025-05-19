# 🕹 Multiplayer Tag Game

## Overview

This is a real-time multiplayer **Tag** game built with Python. Players connect to a central server and play on a 3x3 grid rendered using **Pygame**. One player is randomly chosen as “IT” and tries to tag others by selecting the same grid square. The game continues in rounds until a player has been tagged three times, at which point the game ends.

The system is built using TCP socket programming for communication between the server and clients, and threading is used to manage concurrent gameplay and synchronization across clients.

## 🎯 How the Game Works

- A **server** (`tcp_server.py`) is run to handle all client connections and game state.
- Up to **4 players** can join by running the **client** (`game.py`) script.
- Each round:
  - One player is randomly selected as **IT**.
  - All other players secretly choose a square on the 3x3 grid to hide in.
  - IT chooses a square in an attempt to tag someone.
- If IT picks the same square as any other player, that player is **tagged** and becomes the new IT.
- If no one is tagged, the current IT remains IT for the next round.
- A player who gets tagged **3 times** loses, and the game ends.
- Game state updates are broadcast to all clients in real-time.

## 🚀 How to Run

### Requirements
- Python 3.7 or higher
- Pygame (install with `pip install pygame`)

### Steps

1. Open a terminal and run the server:
   ```bash
   python tcp_server.py
   ```

2. In separate terminals (or on other machines on the same network), run each client:
   ```bash
   python game.py
   ```

3. Once 4 players have joined, the game will begin automatically.

> ⚠️ Make sure all clients connect to the correct server IP (default is `127.0.0.1`). Update the IP in `game.py` if needed for LAN play.

# This code requires the non-standard library numpy
import _thread
import math
import socket
import queue
import numpy as np
from time import sleep
from tkinter import *
from tkinter.ttk import *


# Color values for Pygame
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Information for Pygame Graphics
SQUARE_SIZE = 100
RADIUS = int(SQUARE_SIZE / 2 - 5)
ROW_COUNT = 6
COLUMN_COUNT = 7

# Information for matrix
width = COLUMN_COUNT * SQUARE_SIZE
height = (ROW_COUNT + 1) * SQUARE_SIZE
size = (width, height)


# Function to determine the current ip of machine connects to google dns server and returns ip used to connect
def find_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_address = s.getsockname()[0]
    s.close()
    return local_address


# Function to create a matrix board
def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


# Function to move data and add piece to matrix
def move(board, row, column, piece):
    board[row][column] = piece


# Function to return if matrix is full in column
def is_valid(board, column):
    return board[ROW_COUNT - 1][column] == 0


# Function returns the next open row in column
def get_next_row(board, column):
    for r in range(ROW_COUNT):
        if board[r][column] == 0:
            return r


# Function to determine if move made results in four in a row somewhere in the matrix
def is_winner(board, piece):

    # This for loop checks all possible win conditions horizontally
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and \
                    board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # This for loop checks all possible win conditions vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and \
                    board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # This for loop checks all possible win conditions through negative/descending diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and \
                    board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True

    # This for loop checks all possible win conditions through positive/ascending diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and \
                    board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True


# Function to check matrix to see if full resulting in tie
def is_tie(board):
    for r in board:
        for val in r:
            if val == 0:
                return True
    return False


# Function to start PvP game takes connection address/port queue (for addresses) and queue2 (for moves)
def start_game(connection, address, queue, queue2):
    # print("Starting game!")
    # print_board(board)

    # Create matrix and set turn to first person and game over to false
    board = create_board()
    game_over = False
    turn = 0

    while not game_over:
        # Continue value to insure moves else break
        game_continue = True

        while True:
            # Try to receive game moves
            try:
                # Receive from client the x coordinate of their mouse click
                position_x = int(connection.recv(1024).decode())
                # print('Received {}'.format(position_x))

                # If 9999 received it is AI move and is valid
                if position_x == 9999:
                    # Column is then received from client
                    column_AI = int(connection.recv(1024).decode())

                # If value found break
                if position_x:
                    break

            # If error end game
            except ValueError:
                game_over = True
                game_continue = False
                # print("Game over - Exit")
                break

        if not game_continue:
            break

        # If AI move column set to AI's column else column is calculated with x coordinate
        if position_x == 9999:
            column = column_AI
        else:
            column = int(math.floor(position_x / SQUARE_SIZE))

        # column is then checked to see if it is available
        if is_valid(board, column):
            # print('Sending conformation to client')
            connection.sendall("1".encode())

            # Move column is sent to queue with address of client to move queue
            queue2.put(column)
            queue2.put(address)

            # Player 1
            if turn == 0:
                # Turn information sent to move queue
                queue2.put(1)

                # Matrix updated with move made
                row = get_next_row(board, column)
                move(board, row, column, 1)

                # Matrix is checked for winner
                if is_winner(board, 1):
                    # print("Player 1 wins")
                    game_over = True

                # Matrix is then checked for tie condition
                if not is_tie(board):
                    game_over = True

            # Player 2
            else:
                # Turn information sent to move queue
                queue2.put(2)

                # Matrix updated with move made
                row = get_next_row(board, column)
                move(board, row, column, 2)

                # Matrix is checked for winner
                if is_winner(board, 2):
                    game_over = True

                # Matrix is then checked for tie condition
                if not is_tie(board):
                    game_over = True

            # Turn updated
            turn += 1
            turn = turn % 2

            # If game over winner is received from client and winner/client address added to game status queue
            if game_over:
                # print("game over")
                game_over_conf = str(connection.recv(1024).decode())
                queue.put(game_over_conf)
                queue.put(address)

        # If invalid move notify client
        else:
            # print('Sending invalid to client')
            connection.sendall("0".encode())


# Function for server GUI
def gui(queue, queue2):
    # Variable to track treeview entries
    n = 0

    # Tkinter GUI set up
    root = Tk()
    root.title("Server")
    tree = Treeview(root)

    # Dictionaries for treeview folders and connections
    folder = {}
    connections = {}

    # Function to constantly run updating GUI
    def update_gui(folder, n, connections):
            # If connection queue not empty
            if not queue.empty():
                # Game type pulled form connection queue
                type_of_game = queue.get()

                # If 2 player game
                if type_of_game == '1':
                    # IP pulled from connection queue
                    ip = queue.get()

                    # Folder added to treeview
                    folder[n] = tree.insert('', "end", text=ip, values=("On Going", "2-Player", ""))
                    # print(folder[n])

                    # Connections dictionary updated
                    connections[ip] = n, folder[n], "2-Player"

                    # Num of folders updated
                    n = n + 1

                # If CPU game
                elif type_of_game == '2':
                    # IP pulled from connection queue
                    ip = queue.get()

                    # Folder added to treeview
                    folder[n] = tree.insert('', "end", text=ip, values=("On Going", "CPU-Player", ""))

                    # Connections dictionary updated
                    connections[ip] = n, folder[n], "CPU-Player"

                    # Num of folders updated
                    n = n + 1

                # Game is over player 1 won
                elif type_of_game == '3':
                    # IP pulled from connection queue
                    ip = queue.get()

                    # Pull folder number and id and game type from connections dictionary
                    n, id, game_info = connections[ip]

                    # Update folder info
                    temp = tree.item(id, text=ip, values=("Player 1 Won", game_info))

                # Game is over player 2/cpu won
                elif type_of_game == '4':
                    # Text to update folder with
                    x = "Player 2 Won"

                    # IP pulled from connection queue
                    ip = queue.get()

                    # Pull folder number and id and game type from connections dictionary
                    n, id, game_info = connections[ip]

                    # If game info is computer player update tet to display
                    if game_info == "CPU-Player":
                        x = "CPU Won"

                    # Update folder info
                    temp = tree.item(id, text=ip, values=(x, game_info))

                # Tie result
                elif type_of_game == '5':
                    # IP pulled from connection queue
                    ip = queue.get()

                    # Pull folder number and id and game type from connections dictionary
                    n, id, game_info = connections[ip]

                    # Update folder info
                    temp = tree.item(id, text=ip, values=("Tie", game_info))

                # Not defined response
                else:
                    print("Error")

            # If move queue is not empty
            if not queue2.empty():
                # Get column, ip, and player number
                column = queue2.get()
                ip = queue2.get()
                player_num = queue2.get()
                # print(ip, column, player_num)

                # Examine who made the move by looking at player number
                if player_num == 1:
                    player = "Player 1"
                elif player_num == 2:
                    player = "Player 2"

                # Pull folder number and id and game type from connections dictionary
                n, id, game_info = connections[ip]

                # Insert moves into folder
                tree.insert(id, "end", text=player, values=("Dropped in column", column))

            # return n and connections
            return n, connections

    # Column and heading info for treeview
    tree["columns"] = ("one", "two")
    tree.column("#0", width=270, minwidth=270)
    tree.column("one", width=150, minwidth=150)
    tree.column("two", width=150, minwidth=150)
    tree.heading("#0", text="Connection", anchor=W)
    tree.heading("one", text="Status", anchor=W)
    tree.heading("two", text="Type", anchor=W)
    tree.pack()

    # Loop indefinitely
    while True:
        n, connections = update_gui(folder, n, connections)
        root.update_idletasks()
        root.update()


if __name__ == '__main__':
    # Queue for connections and moves
    client_ips = queue.Queue()
    client_moves = queue.Queue()

    # Local IP, server, and socket
    local_ip_address = find_local()
    server = (local_ip_address, 10000)
    sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Start new GUI thread
    _thread.start_new_thread(gui, (client_ips, client_moves))

    try:
        # Server start
        print('Starting up on {} port {}'.format(*server))
        sok.bind(server)
        sok.listen(5)

        while True:
            # Continually accept connections and start new treads for each connection
            connection, client = sok.accept()
            print('Connection from', client)
            _thread.start_new_thread(start_game, (connection, client, client_ips, client_moves))

            # Get game type from client and store the type and client
            game_type = connection.recv(1024).decode()
            client_ips.put(game_type)
            client_ips.put(client)

    finally:
        # Close connections and sockets
        print('Closing')
        connection.close()
        sok.close()

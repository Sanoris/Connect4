# This code requires the non-standard library numpy and pygame
import math
import socket
import sys
import time
import random
import pygame
import numpy as np
from tkinter import *

# Color values for Pygame
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# Information for Pygame Graphics
SQUARE_SIZE = 100
RADIUS = int(SQUARE_SIZE / 2 - 5)
ROW_COUNT = 6
COLUMN_COUNT = 7
GAME_SELECT = 0

# Game winner info
WINNER = 0
PLAYER_ONE = 1
PLAYER_TWO = 2

# Information for matrix
width = COLUMN_COUNT * SQUARE_SIZE
height = (ROW_COUNT + 1) * SQUARE_SIZE
size = (width, height)
clock = pygame.time.Clock()


# Function to determine the current ip of machine connects to google dns server and returns ip
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


# Function to flip matrix and print it
def print_board(board):
    print(np.flip(board, 0))


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


# Function to draw matrix with pygame
def draw_board(board, screen):
    pygame.display.set_caption("Connect-4")
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARE_SIZE, r * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(screen, BLACK, (
                int(c * SQUARE_SIZE + SQUARE_SIZE / 2), int(r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (
                    int(c * SQUARE_SIZE + SQUARE_SIZE / 2), height - int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, GREEN, (
                    int(c * SQUARE_SIZE + SQUARE_SIZE / 2), height - int(r * SQUARE_SIZE + SQUARE_SIZE / 2)), RADIUS)
    pygame.display.update()


def score_window(window, piece):
    score = 0
    if window.count(piece) == 3 and window.count(0) == 1:
        score += 10
    if window.count(piece) == 2 and window.count(0) == 2:
        score += 1


    if window.count(1) == 2 and window.count(0) == 2:
        score -= 2
    return score


def position_score(board, piece):
    score = 0

    # Center Column strategy
    center_arr = [int(i) for i in list(board[:,3])]
    score += center_arr.count(piece) * 2

    # Score horizontal
    for r in range(ROW_COUNT):
        rows = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT - 3):
            window = rows[c:c+4]
            score += score_window(window, piece)

    # Score vertical
    for c in range(COLUMN_COUNT):
        cols = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT - 3):
            window = cols[c:c+4]
            score += score_window(window, piece)

    # Score Positive Diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += score_window(window, piece)

    # Score Negative Diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+3-i][c-i] for i in range(4)]
            score += score_window(window, piece)
    return score


def get_locations(board):
    valid_locations = []
    for c in range(COLUMN_COUNT):
        if is_valid(board, c):
            valid_locations.append(c)
    return valid_locations


# Simulate dropping a piece then calculate the score of the potential boardstate
def best_move(board, piece):
    best = -9999
    valid_locations = get_locations(board)
    bestspot = random.choice(valid_locations)
    for c in valid_locations:
        tempboard = board.copy()
        move(tempboard, get_next_row(board, c), c, piece)

        score = position_score(tempboard, piece)
        if score > best:
            best = score
            bestspot = c
    return bestspot


def is_terminal(board):
    return is_winner(board, 1) or is_winner(board, 2) or len(get_locations(board)) == 0


def minmax(board, depth, player):
    valid_locations = get_locations(board)
    terminal = is_terminal(board)
    if depth == 0 or terminal:
        if terminal:
            if is_winner(board, 2):
                return None, 99999999
            if is_winner(board, 1):
                return None, -99999999
            else:
                return None, 0
        else:
            return None, position_score(board, 2)
    if player:
        value = -math.inf
        col = random.choice(valid_locations)
        for c in valid_locations:
            tempboard = board.copy()
            move(tempboard, get_next_row(board, c), c, 2)
            score = minmax(tempboard, depth-1, False)[1]
            if score > value:
                value = score
                col = c
        return col, value
    else:
        value = math.inf
        col = random.choice(valid_locations)
        for c in valid_locations:
            tempboard = board.copy()
            move(tempboard, get_next_row(board, c), c, 1)
            score = minmax(tempboard, depth-1, True)[1]
            if score < value:
                value = score
                col = c
        return col, value


# PVE mode computer's turn
# Returns the simulated x-pos of the best move
def AI(board, sok, screen):
    # Initialize the minmax algorithm
    best, score = minmax(board, 4, True)
    # print(best)
    sok.sendall(str(9999).encode())
    sok.sendall(str(best).encode())

    while True:
        conformation = sok.recv(1024).decode()
        if conformation:
            print('Received {} as conformation'.format(conformation))
            break
    row = get_next_row(board, best)
    move(board, row, best, 2)


# PVE mode player's turn
def P1(board, sok, posx):

    while True:
        conformation = sok.recv(1024).decode()
        if conformation:
            print('Received {} as conformation'.format(conformation))
            break

    column = int(math.floor(posx / SQUARE_SIZE))
    if int(conformation) == 1:
            # print(event.pos)
        row = get_next_row(board, column)
        move(board, row, column, 1)


# Function to destroy GUI root
def close(root):
    root.destroy()


# Function to get value of radio button
def selected():
    return var.get()


# Function to change the value of game selected
def game_select():
    global GAME_SELECT
    GAME_SELECT = selected()


# Function to connect to ip using TCP socket
def connect(ip):
    server = (ip, 10000)
    sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print('Connecting to {} port {}'.format(*server))
        sok.connect(server)
        return sok

    except socket.error as err:
        print('Caught exception socket.error : {!r}'.format(err))


def PVE(pygame, game_over, turn, screen, board, myfont, sok):
    winner = 0
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, RED, (posx, int(SQUARE_SIZE / 2)), RADIUS)
            pygame.display.update()

            if turn == 0 and event.type == pygame.MOUSEBUTTONDOWN:
                # print(turn)
                turn += 1
                turn = turn % 2
                posx = event.pos[0]
                sok.sendall(str(posx).encode())
                P1(board, sok, posx)
                label = myfont.render("Please wait", 1, RED)

                if is_winner(board, 1):
                    label = myfont.render("Player 1 wins!", 1, RED)
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                    screen.blit(label, (40, 10))
                    winner = PLAYER_ONE
                    game_over = True

                if not is_tie(board):
                    label = myfont.render("TIE!", 1, BLUE)
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                    screen.blit(label, (40, 10))
                    game_over = True
                draw_board(board, screen)

            if turn == 1 and game_over is False:
                # print(turn)
                turn += 1
                turn = turn % 2
                AI(board, sok, screen)
                if is_winner(board, 2):
                    label = myfont.render("CPU Wins", 1, GREEN)
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                    screen.blit(label, (40, 10))
                    winner = PLAYER_TWO
                    game_over = True

                if not is_tie(board):
                    label = myfont.render("TIE!", 1, BLUE)
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                    screen.blit(label, (40, 10))
                    game_over = True
                draw_board(board, screen)

            if game_over:
                if winner == 1:
                    sok.sendall(str(3).encode())
                elif winner == 2:
                    sok.sendall(str(4).encode())
                else:
                    sok.sendall(str(5).encode())
                winner = 0
                pygame.time.wait(3000)
                print('Closing')
                sok.close()
                pygame.quit()


def PVP(pygame, game_over, turn, screen, board, myfont, sok):
    # Variable to hold winner
    winner = 0

    while not game_over:
        # If window closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Update position of piece on screen
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARE_SIZE / 2)), RADIUS)
                else:
                    pygame.draw.circle(screen, GREEN, (posx, int(SQUARE_SIZE / 2)), RADIUS)

            # Update display
            pygame.display.update()

            # If mouse click send click x coordinate to server
            if event.type == pygame.MOUSEBUTTONDOWN:
                posx = event.pos[0]
                sok.sendall(str(posx).encode())

                # Loop till conformation is received from server
                while True:
                    conformation = sok.recv(1024).decode()
                    if conformation:
                        print('Received {} as conformation'.format(conformation))
                        break

                # column created from pos_x
                column = int(math.floor(posx / SQUARE_SIZE))

                # If move is good
                if int(conformation) == 1:
                    # print(event.pos)

                    # Player 1
                    if turn == 0:
                        # Draw pygame board and make move
                        row = get_next_row(board, column)
                        move(board, row, column, 1)
                        pygame.draw.circle(screen, GREEN, (posx, int(SQUARE_SIZE / 2)), RADIUS)

                        # If player 2 is the winner update game over, pygame screen, and winner value
                        if is_winner(board, 1):
                            label = myfont.render("Player 1 wins!", 1, RED)
                            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                            screen.blit(label, (40, 10))
                            winner = PLAYER_ONE
                            game_over = True

                        # If tie update game over and pygame screen
                        if not is_tie(board):
                            label = myfont.render("TIE!", 1, BLUE)
                            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                            screen.blit(label, (40, 10))
                            game_over = True

                        # print(selection)
                        # print(type(selection))
                        # print_board(board)

                        # Redraw board
                        draw_board(board, screen)

                    # Player 2
                    else:
                        # Draw pygame board and make move
                        row = get_next_row(board, column)
                        move(board, row, column, 2)
                        pygame.draw.circle(screen, RED, (posx, int(SQUARE_SIZE / 2)), RADIUS)

                        # If player 2 is the winner update game over, pygame screen, and winner value
                        if is_winner(board, 2):
                            label = myfont.render("Player 2 wins!", 1, GREEN)
                            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                            screen.blit(label, (40, 10))
                            winner = PLAYER_TWO
                            game_over = True

                        # If tie update game over and pygame screen
                        if not is_tie(board):
                            label = myfont.render("TIE!", 1, BLUE)
                            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
                            screen.blit(label, (270, 10))
                            game_over = True

                        # print(selection)
                        # print(type(selection))
                        # print_board(board)

                        # Draw board again
                        draw_board(board, screen)

                    # Turn updated
                    turn += 1
                    turn = turn % 2

                    # When game over
                    if game_over:
                        # If player one winner send 3 to server
                        if winner == 1:
                            sok.sendall(str(3).encode())
                        # If player two or CPU winner send 4 to server
                        elif winner == 2:
                            sok.sendall(str(4).encode())
                        # Else tie send 5 to server
                        else:
                            sok.sendall(str(5).encode())

                        # Winner reset pygame/socket closed
                        winner = 0
                        pygame.time.wait(3000)
                        # print('Closing')
                        sok.close()
                        pygame.quit()


# Function to set up game and start either pvp game or pve game
def game_start(pygame, ip):

    # Establish socket and game selected
    sok = connect(ip)
    game_select()

    # Create matrix board, set turn, and game not over
    board = create_board()
    game_over = False
    turn = 0

    # Pygame initialize
    pygame.init()
    myfont = pygame.font.SysFont("monospace", 75)
    screen = pygame.display.set_mode(size)
    draw_board(board, screen)
    pygame.display.update()

    # If pvp game
    if GAME_SELECT == 1:
        print("Starting pvp game!")

        # Send game type selection to server and start pvp game
        sok.sendall(str(GAME_SELECT).encode())
        PVP(pygame, game_over, turn, screen, board, myfont, sok)

    # If pve game
    if GAME_SELECT == 2:
        print("Starting pve game!")

        # Send game type selection to server and run pve game
        sok.sendall(str(GAME_SELECT).encode())
        PVE(pygame, game_over, turn, screen, board, myfont, sok)


if __name__ == '__main__':
    try:
        # GUI base
        root = Tk()
        root.title("Client")
        frame = Frame(root)
        root.geometry('250x200')

        # Var for radiobox value
        var = IntVar()
        var.set(1)

        # Entry box
        IPS = Entry(root, width=20)
        IPS.grid(row=2, column=3, columnspan=3, sticky=W+E)

        # Labels and Text boxes for ip and port
        Label(root, anchor=W, text="Enter IP of Server:").grid(row=1, column=3, columnspan=3, sticky=W)
        Radiobutton(root, anchor=W, text="2-Player:", variable=var, value=1, width=15).grid(row=4, column=3, sticky=W, columnspan=4)
        Radiobutton(root, anchor=W, text="CPU-Player:", variable=var, value=2, width=15).grid(row=5, column=3, sticky=W, columnspan=4)

        # Grid configuration
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(7, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(4, weight=1)
        root.grid_columnconfigure(6, weight=1)

        # quit and play buttons
        Button(root, text='Play', command=lambda: game_start(pygame, str(IPS.get())), width=8).grid(row=6, column=5, sticky=W, pady=4)
        Button(root, text='Quit', command=root.quit, width=8).grid(row=6, column=3, sticky=W, pady=4)

        # end GUI
        root.mainloop()

    finally:
        # Closing client
        print('Closing')
"""
Tic Tac Toe Player
"""

import math
import copy    #I had to import this to make a deep copy 

X = "X"
O = "O"
EMPTY = None

#Creating recursive functions for minimax
def max_value(board):
    """
    Returns value of the board
    """

    if terminal(board) == True:
        return utility(board)
    v = -10000
    for a in actions(board):
        v = max(v, min_value(result(board, a)))
    return v

def min_value(board):
    
    if terminal(board) == True:
        return utility(board)
    v = 10000
    for a in actions(board):
        v = min(v, max_value(result(board, a)))
    return v


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state():
        return X
    count_x = 0
    count_o = 0
    for i in range(0, 3):
        for j in range(0, 3):
            if board[i][j] == X:
                count_x += 1
            if board[i][j] == O:
                count_o += 1
    if count_o < count_x:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    choices = set()
    for i in range (0, 3):
        for j in range(0, 3):
            if board[i][j] == EMPTY:
                choices.add((i, j))
    return choices


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception
    else:
        board_copy = copy.deepcopy(board)    #Deep copy
        
        if player(board) == X:
            board_copy[list(action)[0]][list(action)[1]] = X   #extracting i and j from (i, j) tuple
            return board_copy
        else:
            board_copy[list(action)[0]][list(action)[1]] = O
            return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    while True:
        #Horizontal wins
        for i in range(0, 3):
            if board[i][0] == board[i][1] == board[i][2] == X:
                return X
            elif board[i][0] == board[i][1] == board[i][2] == O:
                return O
        #Vertical wins
        for j in range(0, 3):
            if board[0][j] == board[1][j] == board[2][j] == X:
                return X
            elif board[0][j] == board[1][j] == board[2][j] == O:
                return O
        #Diagonal wins
        if board[0][0] == board[1][1] == board[2][2] == X:
            return X
        if board[0][0] == board[1][1] == board[2][2] == O:
            return O
        
        if board[0][2] == board[1][1] == board[2][0] == X:
            return X
        elif board[0][2] == board[1][1] == board[2][0] == O:
            return O
        
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    elif board == initial_state():
        return False
    else:
        if len(actions(board)) > 0:
            return False
        else:
            return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board) == True:
        return None
    else:
        if player(board) == O:
            var = 1   #dummy variable initialized at highest value possible 
            for a in actions(board):
                if max_value(result(board, a)) <= var:   #Player-O wants lowest of the maximums
                    var = max_value(result(board, a))
                    optimal_action = a
            return optimal_action
                
        elif player(board) == X:
            var = -1   #same as above but at the lowest value possible
            for a in actions(board):
                if min_value(result(board, a)) >= var:   #Player-X wants highest of the minimums
                    var = min_value(result(board, a))
                    optimal_action = a
            return optimal_action

from itertools import chain
import numpy as np
import random

class RP(object):
    def __init__(self, player, board=[]):
        if len(board) == 0:
            self.board = self.input_board()
        else:
            self.board = board
        self.color_base = self.fix_color_base()
        self.player = player
        
    def input_board(self):
        board = np.zeros((7, 7), dtype=int)
        for row in range(7):
            board[row] = input().split()
        print()
        return board
        
    def fix_color_base(self, board=[]):
        if len(board) == 0:
            board = self.board
        color_base = []
        # 降維
        dr = list(chain.from_iterable(board))
        for i in range(1, 8):
            color_base.append([i] * (7 - dr.count(i)))
        color_base = list(chain.from_iterable(color_base))
        random.shuffle(color_base)
        color_base = list(color_base)
        return color_base
    
    def readable(self, position):
        return chr(position[0] + 65), chr(position[1] + 97)
    
    def print_board(self):
        print("  ", end="")
        for col in range(7):
            print(chr(col + 97), end=" ")
        print()
        for row in range(7):
            print(chr(row + 65), end=" ")
            for col in range(7):
                print(self.board[row][col], end=" ")
            print()
        print()   
        
    def move(self, now_player, color, source, dest=None):
        b = self.board
        if now_player == "CHAOS":
            b[source[0]][source[1]] = color
        else:
            tmp = b[source[0]][source[1]]
            b[source[0]][source[1]] = b[dest[0]][dest[1]]
            b[dest[0]][dest[1]] = tmp
        return b

    def chaos(self):
        color = self.color_base.pop()
        positions = np.where(self.board == 0)
        indices = list(zip(positions[0], positions[1]))
        random.shuffle(indices)

        choose = indices.pop()
        self.board = self.move(now_player="CHAOS", color=color, source=choose)
        print("Choose", color, "at", self.readable(choose))
        self.print_board()

    def order(self):
        positions = np.where(self.board != 0)
        indices = list(zip(positions[0], positions[1]))
        random.shuffle(indices)

        choose = indices.pop()
        indices = [choose]
        row_pair, col_pair = [[choose[0] - 1, -1, -1], [choose[0] + 1, 7, 1]], [
            [choose[1] - 1, -1, -1],
            [choose[1] + 1, 7, 1],
        ]
        for i in range(2):
            for j in range(row_pair[i][0], row_pair[i][1], row_pair[i][2]):
                if self.board[j][choose[1]] != 0:
                    break
                indices.append((j, choose[1]))
            for j in range(col_pair[i][0], col_pair[i][1], col_pair[i][2]):
                if self.board[choose[0]][j] != 0:
                    break
                indices.append((choose[0], j))
        random.shuffle(indices)

        dest = indices.pop()
        self.board = self.move(now_player="ORDER", color=0, source=choose, dest=dest)
        print("From", self.readable(choose), "to", self.readable(dest))
        self.print_board()

    def is_game_over(self):
        return True if len(self.color_base) == 0 else False

# player = input("Player: ")
# RP = RP(player=player)
# RP.print_board()
# if player == "CHAOS":
#     RP.chaos()
# while not RP.is_game_over():
#     RP.order()
#     RP.chaos()

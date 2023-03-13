import numpy as np
import copy 
import time
import MCTS
import simulate

mcts_start, mcts_end = 25, 40
start = time.time()

class Node(object):
    def __init__(self, player):
        self.board = np.zeros((7, 7), dtype=int)
        self.player = player
        
    def get_chaos_actions(self):
        positions = np.where(self.board == 0)
        actions = list(zip(positions[0], positions[1]))
        return actions
    
    def get_order_actions(self):
        positions = np.where(self.board != 0)
        sources = list(zip(positions[0], positions[1]))
        actions = []
        
        for action in sources:
            row, col = action[0], action[1]
            row_pair = [[row - 1, -1, -1], [row + 1, 7, 1]]
            col_pair = [[col - 1, -1, -1], [col + 1, 7, 1]]
            for i in range(2):
                for j in range(row_pair[i][0], row_pair[i][1], row_pair[i][2]):
                    if self.board[j][col] != 0:
                        break
                    actions.append((action[0], action[1], j, col))
                for j in range(col_pair[i][0], col_pair[i][1], col_pair[i][2]):
                    if self.board[row][j] != 0:
                        break
                    actions.append((action[0], action[1], row, j))
        return actions
    
    def _rule(self, actions):
        return actions[np.random.randint(len(actions))]
    
    def move(self, source, dest=None, color=0):
        b = self.board
        if dest == None:
            b[source[0]][source[1]] = color
            return b
        else:
            tmp = b[source[0]][source[1]]
            b[source[0]][source[1]] = b[dest[0]][dest[1]] 
            b[dest[0]][dest[1]] = tmp
            return b
    
    def is_game_over(self):
        return True if len(np.where(self.board == 0)[0]) == 0 else False
    
    def print_board(self):
        board = self.board
        print("  ", end="")
        for col in range(7):
            print(chr(col + 97), end=" ")
        print()
        for row in range(7):
            print(chr(row + 65), end=" ")
            for col in range(7):
                print(board[row][col], end=" ")
            print()
        print() 
    
class Format():    
    def chaos_type(input):
        return int(input[0]), (ord(input[1])-65, ord(input[2])-97)
    
    def order_type(input):
        return (ord(input[0])-65, ord(input[1])-97, ord(input[2])-65, ord(input[3])-97)
    
    def print_chaos_action(action):
        print(chr(action[0]+65)+chr(action[1]+97))
        return
    
    def print_order_action(action):
        print(chr(action[0]+65)+chr(action[1]+97)+chr(action[2]+65)+chr(action[3]+97))
        return   
    

def main():
    Input = input()
    root = Node(player='CHAOS')
    chess_num = 0
    if Input != 'Start':
        root.player = 'ORDER'        
        while Input != 'Quit':
            color, opponent_action = Format.chaos_type(input=Input)
            root.move(source=opponent_action, color=color)
            # root.print_board()
            chess_num += 1
            
            if chess_num < mcts_start or chess_num > mcts_end:
                actions = root.get_order_actions()
                action = root._rule(actions)          
                root.move(source=action[:2], dest=action[2:])
                if __debug__ == False:
                    root.print_board()
                Format.print_order_action(action)
            else:
                action = mcts_rule(player=root.player, board=root.board)
                root.move(source=action[:2], dest=action[2:])
                if __debug__ == False:
                    root.print_board()
                Format.print_order_action(action)
            Input = input()
    else:
        while (1):
            Input = input()
            if chess_num < mcts_start or chess_num > mcts_end:
                actions = root.get_chaos_actions()
                action = root._rule(actions)          
                root.move(source=action, color=int(Input))
                if __debug__ == False:
                    root.print_board()
                Format.print_chaos_action(action)
            else:
                action = mcts_rule(player=root.player, board=root.board, color=int(Input))
                root.move(source=action, color=int(Input))
                if __debug__ == False:
                    root.print_board()
                Format.print_chaos_action(action)
            chess_num += 1
            
            Input = input()   
            if Input == 'Quit':
                break         
            opponent_action = Format.order_type(input=Input)
            root.move(source=opponent_action[:2], dest=opponent_action[2:])
            
def mcts_rule(player, board, color=0):
    # print('----------------------------MCTS-----------------------------')
    game = simulate.RP(player=player, board=board)
    root = MCTS.MCTS_Node(board=game.board, main_player=player, color_base=game.color_base, color=color)
    selected_node = root.best_action()
    return selected_node.parent_action    
main()
    
   
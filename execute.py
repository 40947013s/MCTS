import MCTS
import MCTS_mid
import numpy as np
from copy import deepcopy

class Node(object):
    def __init__(self, player):
        self.board = np.zeros((7, 7), dtype=int)
        self.player = player   
            
    def get_score(self, board=[]):
        score = 0 
        if len(board) == 0:
            board = self.board
        for k in range(2, 8):
            for i in range(7):
                for j in range(8-k):
                    if k <= 3:
                        if board[i][j] == 0:
                            continue
                        if board[i][j+ 1 + (k % 2)] == board[i][j]:
                            score += k
                    elif k <= 5:
                        if board[i][j] == 0 or board[i][j + 1] == 0:
                            continue
                        if board[i][j + 2 + (k % 2)] == board[i][j + 1] and board[i][j + 3 + (k % 2)] == board[i][j]:
                            score += k
                    else:
                        if board[i][j] == 0 or board[i][j + 1] == 0 or board[i][j + 2] == 0:
                            continue
                        if board[i][j + 3 + (k % 2)] == board[i][j + 2] and board[i][j + 4 + (k % 2)] == board[i][j + 1] and board[i][j + 5 + (k % 2)] == board[i][j]:
                            score += k
        for k in range(2, 8):
            for j in range(7):
                for i in range(8-k):
                    if k <= 3:
                        if board[i][j] == 0:
                            continue
                        if board[i+ 1 + (k % 2)][j] == board[i][j]:
                            score += k
                    elif k <= 5:
                        if board[i][j] == 0 or board[i + 1][j] == 0:
                            continue
                        if board[i + 2 + (k % 2)][j] == board[i + 1][j] and board[i + 3 + (k % 2)][j] == board[i][j]:
                            score += k
                    else:
                        if board[i][j] == 0 or board[i + 1][j] == 0 or board[i + 2][j] == 0:
                            continue
                        if board[i + 3 + (k % 2)][j] == board[i + 2][j] and board[i + 4 + (k % 2)][j] == board[i + 1][j] and board[i + 5 + (k % 2)][j] == board[i][j]:
                            score += k
        return score
    
    def last(self, row, col):
        score = 0
        max_score = self.get_score()
        max_row, max_col = row, col
        for i in range(1, 7-col):
            if self.board[row][col + i] == 0:
                self.move([row, col], [row, col+i])
                score = self.get_score();
                if score > max_score:
                    max_score = deepcopy(score)
                    max_row = deepcopy(row)
                    max_col = deepcopy(col + i)
                self.move([row, col+i], [row, col])
            else:
                break
        for i in range(1, col+1):
            if self.board[row][col - i] == 0:
                self.move([row, col], [row, col-i])
                score = self.get_score();
                if score > max_score:
                    max_score = deepcopy(score)
                    max_row = deepcopy(row)
                    max_col = deepcopy(col - i)
                self.move([row, col-i], [row, col])
            else:
                break
        for i in range(1, row+1):
            if self.board[row - i][col] == 0:
                self.move([row, col], [row-i, col])
                score = self.get_score()
                if score > max_score:
                    max_score = deepcopy(score)
                    max_row = deepcopy(row - i)
                    max_col = deepcopy(col)
                self.move([row-i, col], [row, col])
            else:
                break
        for i in range(1, 7-row):
            if self.board[row + i][col] == 0:
                self.move([row, col], [row+i, col])
                score = self.get_score()
                if score > max_score:
                    max_score = deepcopy(score)
                    max_row = deepcopy(row + i)
                    max_col = deepcopy(col)
                self.move([row+i, col], [row, col])
            else:
                break
        return row, col, max_row, max_col
        
    def _rule(self, actions):
        idx = np.random.randint(len(actions))
        return idx, actions[idx]
    
    def _rule2(self, last_action=[]):
        positions = np.where(self.board != 0)
        sources = list(zip(positions[0], positions[1]))
        ori_score = self.get_score()
        actions, gap_list = [], []   
        for action in sources:
            for i in range(action[0]-1, -1, -1):
                if self.board[i][action[1]] != 0:
                    break                
                self.move(action, [i, action[1]])
                score = self.get_score() + 0.1 * abs(i-3) + 0.6 * (np.count_nonzero(self.board[i, :] == self.board[i][action[1]])-1)                                  
                neighbors = [[i+1, action[1]], [i-1, action[1]], [i, action[1]+1], [i, action[1]-1]]
                for neighbor in neighbors:
                    try:
                        if self.board[i][action[1]] == self.board[neighbor[0]][neighbor[1]]:
                            score += 2.1
                    except:
                        pass
                self.move([i, action[1]], action)           
                actions.append((action[0], action[1], i, action[1]))         
                gap_list.append(score)
            for i in range(action[0]+1, 7):
                if self.board[i][action[1]] != 0:
                    break
                self.move(action, [i, action[1]])
                score = self.get_score() + 0.1 * abs(i-3) + 0.6 * (np.count_nonzero(self.board[i, :] == self.board[i][action[1]])-1)           
                neighbors = [[i+1, action[1]], [i-1, action[1]], [i, action[1]+1], [i, action[1]-1]]
                for neighbor in neighbors:
                    try:
                        if self.board[i][action[1]] == self.board[neighbor[0]][neighbor[1]]:
                            score += 2.1
                    except:
                        pass
                self.move([i, action[1]], action)        
                actions.append((action[0], action[1], i, action[1]))       
                gap_list.append(score)    
            for i in range(action[1]-1, -1, -1):
                if self.board[action[0]][i] != 0:
                    break
                self.move(action, [action[0], i])
                score = self.get_score() + 0.1 * abs(i-3) + 0.6 * (np.count_nonzero(self.board[:, i] == self.board[action[0]][i])-1)              
                neighbors = [[action[0]+1, i], [action[0]-1, i], [action[0], i+1], [action[0], i-1]]
                for neighbor in neighbors:
                    try:
                        if self.board[action[0]][i] == self.board[neighbor[0]][neighbor[1]]:
                            score += 2.1
                    except:
                        pass
                self.move([action[0], i], action)        
                actions.append((action[0], action[1], action[0], i))     
                gap_list.append(score)        
            for i in range(action[1]+1, 7):
                if self.board[action[0]][i] != 0:
                    break
                self.move(action, [action[0], i])
                score = self.get_score() + 0.1 * abs(i-3) + 0.6 * (np.count_nonzero(self.board[:, i] == self.board[action[0]][i])-1)                           
                neighbors = [[action[0]+1, i], [action[0]-1, i], [action[0], i+1], [action[0], i-1]]
                for neighbor in neighbors:
                    try:
                        if self.board[action[0]][i] == self.board[neighbor[0]][neighbor[1]]:
                            score += 2.1
                    except:
                        pass
                self.move([action[0], i], action)        
                actions.append((action[0], action[1], action[0], i))
                gap_list.append(score)
                
        for i in range(len(actions)):
            if last_action[:2] == actions[i][2:] and last_action[2:] == actions[i][:2]:
                gap_list[i] -= 5

        gaps = np.array(gap_list)        
        if gaps.max() < ori_score:
            return ((sources[0][0], sources[0][1], sources[0][0], sources[0][1]))
        idx = np.random.choice(np.flatnonzero(gaps == gaps.max()))
        return actions[idx]
    
    def _rule3(self, color) :
        min_c, min_r = 0, 0
        min = 5000
        # 大十字，提高優先權
        score = np.zeros((7, 7), dtype=int)
        score[:, 3] -= 10
        score[3, :] -= 10
        
        up_left, up_right, down_left, down_right = 0, 0, 0, 0
        for row in range(7):
            for col in range(7):
                if self.board[row][col] == 0: 
                    if row <= 2 and col <= 2:
                        up_left += 1
                    elif row <= 2 and col >= 4:
                        up_right += 1
                    elif row >= 4 and col <= 2:
                        down_left += 1
                    elif row >= 4 and col >= 4:
                        down_right += 1
 
        order_may_move = np.zeros((7, 7), dtype=int)
        tmp = np.zeros(4)
        for row in range(7):
            for col in range(7): 
                if self.board[row][col] != 0:
                    # 有棋子的地方分數設1000
                    score[row][col] = 10000
                    # 尋找該棋子最可能的下一步
                    action = self.last(row=row, col=col)
                    self.move(action[:2], action[2:])
                    # 減少下一步位置chaos下的score(增加優先值)
                    score[action[2]][action[3]] -= self.get_score() * 10

                    self.move(action[2:], action[:2])
                    if self.board[row][col] == color:
                        i2, i1, i0, i1_, i2_ = 40, 30, 30, 30, 40
                        j2 , j1, j0, j1_, j2_ = 40, 30, 30, 30, 40
                        i2b, i1b, i0b, i1_b, i2_b = 0, 0, 0, 0, 0
                        j2b, j1b, j0b, j1_b, j2_b = 0, 0, 0, 0, 0

                        for k in range(col, -1, -1): 
                            if row >= 2:
                                if self.board[row - 2][k] == 0:
                                    score[row - 2][k] += i2
                                else:
                                    i2b += 1
                                if i2b == 2:
                                    i2 -= 20                        
                            if row:
                                if self.board[row - 1][k] == 0:
                                    score[row - 1][k] += i1
                                else:
                                    i1b += 1
                                if i1b == 2:
                                    i1 -= 20
                            
                            if self.board[row][k] == 0:
                                score[row][k] += i0
                            elif k != col:
                                i0b += 1
                            if i0b == 2:
                                i0 -= 20
                            if row != 6:
                                if self.board[row + 1][k] == 0:
                                    score[row + 1][k] += i1_
                                else:
                                    i1_b += 1
                                if i1_b == 2:
                                    i1_ -= 20
                            
                            if row <= 4:
                                if self.board[row + 2][k] == 0:
                                    score[row + 2][k] += i2_
                                else:
                                    i2_b += 1
                                if i2_b == 2:
                                    i2_ -= 20
                            
                        i2, i1, i0, i1_, i2_ = 40, 30, 30, 30, 40
                        i2b, i1b, i0b, i1_b, i2_b = 0, 0, 0, 0, 0
                        for k in range(col, 7): 
                            if row >= 2: 
                                if self.board[row - 2][k] == 0:
                                    score[row - 2][k] += i2
                                else:
                                    i2b += 1
                                if i2b == 2:
                                    i2 -= 20                            
                            if row: 
                                if self.board[row - 1][k] == 0:
                                    score[row - 1][k] += i1
                                else:
                                    i1b += 1
                                if i1b == 2:
                                    i1 -= 20
                            
                            if self.board[row][k] == 0:
                                score[row][k] += i0
                            elif k != col:
                                i0b += 1
                            if i0b == 2:
                                i0 -= 20
                            if row != 6: 
                                if self.board[row + 1][k] == 0:
                                    score[row + 1][k] += i1_
                                else:
                                    i1_b += 1
                                if i1_b == 2:
                                    i1_ -= 20
                            
                            if row <= 4: 
                                if self.board[row + 2][k] == 0:
                                    score[row + 2][k] += i2_
                                else:
                                    i2_b += 1
                                if i2_b == 2:
                                    i2_ -= 20

                        for k in range(row, -1, -1):
                            if col >= 2: 
                                if self.board[k][col - 2] == 0:
                                    score[k][col - 2] += j2
                                else:
                                    j2b += 1
                                if j2b == 2:
                                    j2 -= 20  
                            if col: 
                                if self.board[k][col - 1] == 0:
                                    score[k][col - 1] += j1
                                else:
                                    j1b += 1
                                if j1b == 2:
                                    j1 -= 20
                            if self.board[k][col] == 0:
                                score[k][col] += j0
                            elif k != row:
                                j0b += 1
                            if j0b == 2:
                                j0 -= 2
                            if col != 6: 
                                if self.board[k][col + 1] == 0:
                                    score[k][col + 1] += j1_
                                else:
                                    j1_b += 1
                                if j1_b == 2:
                                    j1_ -= 20
                            
                            if col <= 4: 
                                if self.board[k][col + 2] == 0:
                                    score[k][col + 2] += j2_
                                else:
                                    j2_b += 1
                                if j2_b == 2:
                                    j2_ -= 20
        
                        j2, j1, j0, j1_, j2_ = 40, 30, 30, 30, 40
                        j2b, j1b, j0b, j1_b, j2_b = 0, 0, 0, 0, 0

                        for k in range(row, 7):
                            if col >= 2: 
                                if self.board[k][col - 2] == 0:
                                    score[k][col - 2] += j2
                                else:
                                    j2b += 1
                                if j2b == 2:
                                    j2 -= 20
                            if col: 
                                if self.board[k][col - 1] == 0:
                                    score[k][col - 1] += j1
                                else:
                                    j1b += 1
                                if j1b == 2:
                                    j1 -= 20
                            if self.board[k][col] == 0:
                                score[k][col] += j0
                            elif k != row:
                                j0b += 1
                            if j0b == 2:
                                j0 -= 20
                            if col != 6: 
                                if self.board[k][col + 1] == 0:
                                    score[k][col + 1] += j1_
                                else:
                                    j1_b += 1
                                if j1_b == 2:
                                    j1_ -= 20
                            if col <= 4: 
                                if self.board[k][col + 2] == 0:
                                    score[k][col + 2] += j2_
                                else:
                                    j2_b += 1
                                if j2_b == 2:
                                    j2_ -= 20
                else: 
                    # empty，計算可能得分加到score(減少優先權)
                    self.move(source=[row, col], color=color)
                    score[row][col] += self.get_score() * 10
                    self.move(source=[row, col], color=0)
                    # 擁擠度和優先權成正比
                    if row <= 2 and col <= 2:
                        score[row][col] -= up_left
                    elif row <= 2 and col >= 4:
                        score[row][col] -= up_right
                    elif row >= 4 and col <= 2:
                        score[row][col] -= down_left
                    elif row >= 4 and col >= 4:
                        score[row][col] -= down_right
                
        for row in range(7):
            for col in range(7): 
                if min > score[row][col]: 
                    min = deepcopy(score[row][col])
                    min_row, min_col = row, col      
        return min_row, min_col
    
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
    chess_num, last_aciton = 0, []
    
    if Input != 'Start':
        mcts_start, mcts_end = 15, 40        
        root.player = 'ORDER'        
        while Input != 'Quit':
            color, opponent_action = Format.chaos_type(input=Input)
            root.move(source=opponent_action, color=color)
            chess_num += 1
            
            action = []
            if (mcts_start <= chess_num <= mcts_end) and chess_num % 4 == 0:
                action = order_rule(player=root.player, chess_num=chess_num, board=root.board, simulate_time=2850)  
            else:
                action = root._rule2(last_aciton)   
                last_aciton = action
            root.move(source=action[:2], dest=action[2:])
            Format.print_order_action(action)
            Input = input()
    else:
        mcts_start, mcts_end = 36, 42     
        while 1:
            Input = input()
            action = []
            if chess_num < mcts_start or chess_num > mcts_end:
                action = root._rule3(color=int(Input))
            else:
                action = chaos_rule(player=root.player, board=root.board, color=int(Input), simulate_time=5000)
            root.move(source=action, color=int(Input))
            Format.print_chaos_action(action)
            chess_num += 1
            
            Input = input()   
            if Input == 'Quit':
                break         
            opponent_action = Format.order_type(input=Input)
            root.move(source=opponent_action[:2], dest=opponent_action[2:])
            
def order_rule(player, board, chess_num, color=0, simulate_time=1000):
    game = MCTS_mid.RP(player=player, board=board)
    root = MCTS_mid.MCTS_Middle(board=game.board, main_player=player, color_base=game.color_base, mode=chess_num, color=color)
    selected_node = root.best_action(simulate_time=simulate_time)
    return selected_node.parent_action    

def chaos_rule(player, board, color=0, simulate_time=1000):
    game = MCTS.RP(player=player, board=board)
    root = MCTS.MCTS_Node(board=game.board, main_player=player, color_base=game.color_base, color=color)
    selected_node = root.best_action(simulate_time=simulate_time)
    return selected_node.parent_action    
main()
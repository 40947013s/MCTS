import sys
import copy
import numpy as np
from collections import defaultdict
import simulate

class MCTS_Node(object):
    def __init__(self, board, main_player, color_base, color=0, simu_player=None, parent=None, parent_action=None):
        self.board = board
        self.main_player = main_player
        if simu_player == 'CHAOS':
            self.color = color if color != 0 else color_base.pop()
        elif simu_player == 'ORDER':
            self.color = 0
        else:
            self.color = color
        self.color_base = color_base  
        
        self.simu_player = simu_player        
        self.parent = parent
        self.parent_action = parent_action
        
        self.visited_time = 0
        self.children = None
        self.children = []
        self.game_results = defaultdict(int)
        self.game_results[-1] = 0
        self.game_results[1] = 0
        self.unpassed_actions = None
        self.unpassed_actions = self.get_legal_actions()
        
    # 取得合法動作 
    def get_legal_actions(self):
        # 現在是模擬玩家
        player = copy.deepcopy(self.main_player)
        if self.simu_player != None:
            player = self.simu_player
        if player == 'CHAOS':
            return self.get_chaos_actions()
        elif player == 'ORDER':
            return self.get_order_actions()
        else:
            return None
            
    # chaos的合法下棋
    def get_chaos_actions(self):
        positions = np.where(self.board == 0)
        actions = list(zip(positions[0], positions[1]))
        return actions
    
    # order的合法下棋
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
    
    # 勝場數-敗場數
    def q(self):
        return self.game_results[1] - self.game_results[-1]
    
    # 節點拜訪次數
    def n(self):
        return self.visited_time

    '''
    擴展:
        推出一合法動作
        並移動棋盤
    '''
    def expand(self):
        is_used = True
        while(is_used):
            current_node = self
            is_used = False
            if len(current_node.unpassed_actions) == 0:
                return None
            action = current_node.unpassed_actions.pop()
            moved_board = current_node.move(color=self.color, source=action[:2], dest=action[2:])

            # 關注!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            player = copy.deepcopy(current_node.main_player)
            if current_node.simu_player != None:
                player = current_node.simu_player
            
            if player == 'ORDER':
                simu_player = 'CHAOS'
            else:
                simu_player = 'ORDER'
            
            for child in current_node.children:
                if child.parent_action == action:
                    is_used = True
            
        child_node = MCTS_Node(board=moved_board, color_base=copy.deepcopy(current_node.color_base), main_player=current_node.main_player, simu_player=simu_player, parent=current_node, parent_action=action)    
        current_node.children.append(child_node)
        return child_node
    
    # 遊戲是否結束
    def is_game_over(self):
        # 待改
        return True if len(np.where(self.board == 0)[0]) < 7 else False        
    
    # 印出棋盤
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
        
    # 移動棋盤
    def move(self, color, source, dest=None):
        b = copy.deepcopy(self.board)
        
        player = copy.deepcopy(self.main_player)
        if self.simu_player != None:
            player = self.simu_player
        
        if player == 'CHAOS':
            b[source[0]][source[1]] = color
            return b
        elif player == 'ORDER':
            tmp = b[source[0]][source[1]]
            b[source[0]][source[1]] = b[dest[0]][dest[1]] 
            b[dest[0]][dest[1]] = tmp
            return b
        
    def rollout(self):
        current_node = self
        while not current_node.is_game_over():         
            actions = current_node.get_legal_actions()
            action = self.rollout_rule(actions)
            # print(action, current_node.simu_player)
            moved_board = current_node.move(color=self.color, source=action[:2], dest=action[2:])
            current_node.board = moved_board
            # current_node.print_board()
            
            if current_node.simu_player == 'CHAOS':
                current_node.simu_player = 'ORDER'
            else:
                current_node.simu_player = 'CHAOS'
                current_node.color = current_node.color_base.pop()
            # print(current_node.simu_player)
            # print('---------------------------------------------------------------------------')

            # player = copy.deepcopy(current_node.main_player)   
            # if current_node.simu_player != None:
            #     player = current_node.simu_player      
                      
            # simu_player = 'CHAOS' if player == 'ORDER' else 'ORDER'   
            
            # child_node = MCTS_Node(board=moved_board, color_base=copy.deepcopy(current_node.color_base), main_player=self.main_player, simu_player=simu_player, parent=current_node, parent_action=action, floor=current_node.floor)    
        return current_node.game_result()
            
    def rollout_rule(self, actions):
        return actions[np.random.randint(len(actions))]
    
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
    
    def early_end(self):
        game = simulate.RP(player=self.main_player, board=copy.deepcopy(self.board))
        
        for row in range(7):
            for col in range(7):
                if game.board[row][col] == 0:
                    game.board[row][col] = game.color_base.pop()
        return game.board
    
    def game_result(self):    
        board = self.early_end() 
        score = self.get_score(board)
        if score == 80:
            return 0
        if self.main_player == 'CHAOS':
            return -1 if score > 80 else 1
        else:
            return -1 if score < 80 else 1
        
    def backpropagate(self, result):
        self.visited_time += 1
        self.game_results[result] += 1
        if self.parent:
            self.parent.backpropagate(result)   
            
    def is_fully_expanded(self):
        return len(self.unpassed_actions) == 0
    
    def select(self, c=1.96):
        ucb_array = []
        for child in self.children:
            if child.q() != 0:
                ucb_array.append((child.q() / child.n()) + c * np.sqrt((2 * np.log(self.n()) / child.n())))
            else:
                # for i in range (len(self.children)):   
                #     print(self.children[i].n(), self.children[i].parent_action, end=' ')
                # print()
                # self.print_board()
                ucb_array.append((child.q() / 1) + c * np.sqrt((2 * np.log(self.n()) / 1)))
        return self.children[np.argmax(ucb_array)]
    
    def tree_rule(self, i):
        current_node = self
        while not current_node.is_game_over():         
            if not current_node.is_fully_expanded():
                new_node = current_node.expand()
                if new_node == None:    
                    current_node = current_node.select()
                else:  
                    return new_node
            else:
                current_node = current_node.select()
        return current_node
    
    def best_action(self, simulate_time = 1000):        
        for i in range(simulate_time):
            # print(i)
            
            # expansion
            node = self.tree_rule(i)
            # print(type(node))
            
            # simulation
            result = node.rollout()
            #backpropagation
            node.backpropagate(result)
        return self.select()

def main():
    player = 'ORDER'
    game = simulate.RP(player=player)
    root = MCTS_Node(board=game.board, main_player=player, color_base=game.color_base, color=1)
    selected_node = root.best_action()
    print('final', selected_node.parent_action)
    selected_node.board = game.board
    selected_node.print_board()
    return 
    
if __debug__ == False:
    main()

# player = 'CHAOS'
# game = simulate.RP(player=player)
# root = MCTS_Node(board=game.board, main_player=player, color_base=game.color_base, color=1)

# print(root.game_result())
    

                              
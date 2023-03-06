import copy
import numpy as np
from collections import defaultdict
import simulate

class MCTS_Node(object):
    def __init__(self, board, main_player, color_base, color=0, simu_player=None, parent=None, parent_action=None):
        self.board = copy.deepcopy(board)
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
        並移動棋盤elf.move
    '''
    def expand(self):
        action = self.unpassed_actions.pop()
        moved_board = self.move(source=action[:2], dest=action[2:])

        # 關注!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        player = copy.deepcopy(self.main_player)
        if self.simu_player != None:
            player = self.simu_player
            
        simu_player = 'CHAOS' if player == 'ORDER' else 'ORDER'
        child_node = MCTS_Node(board=moved_board, color_base=copy.deepcopy(self.color_base), main_player=self.main_player, simu_player=simu_player, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node
    
    # 遊戲是否結束
    def is_game_over(self):
        return True if len(np.where(self.board == 0)[0]) == 0 else False
    
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
    def move(self, source, dest=None):
        b = copy.deepcopy(self.board)
        
        player = copy.deepcopy(self.main_player)
        if self.simu_player != None:
            player = self.simu_player
        
        if player == 'CHAOS':
            b[source[0]][source[1]] = self.color
            return b
        elif player == 'ORDER':
            tmp = b[source[0]][source[1]]
            b[source[0]][source[1]] = b[dest[0]][dest[1]] 
            b[dest[0]][dest[1]] = tmp
            return b
        
        
    def rollout(self):
        # current_node = copy.deepcopy(self)  
        current_node = self
        while (1):
            if current_node.is_game_over():
                break            
            actions = current_node.get_legal_actions()
            action = current_node.rollout_rule(actions)
            moved_board = current_node.move(source=action[:2], dest=action[2:])
            
            player = copy.deepcopy(current_node.main_player)   
            if current_node.simu_player != None:
                player = current_node.simu_player      
                      
            simu_player = 'CHAOS' if player == 'ORDER' else 'ORDER'   
            
            child_node = MCTS_Node(board=moved_board, color_base=copy.deepcopy(current_node.color_base), main_player=self.main_player, simu_player=simu_player, parent=current_node, parent_action=action)
            current_node.children.append(child_node)
            current_node = current_node.children[0]
        return current_node.game_result()
            
    def rollout_rule(self, actions):
        return actions[np.random.randint(len(actions))]
    
    def get_score(self):
        score = 0 
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
    
    def game_result(self):     
        score = self.get_score()
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
        ucb_array = [(child.q() / child.n()) + c * np.sqrt((2 * np.log(self.n()) / child.n())) for child in self.children]
        return self.children[np.argmax(ucb_array)]
    
    def tree_rule(self):
        current_node = self
        while not current_node.is_game_over():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.select()
        return current_node
    
    def best_action(self):
        simulate_time = 70
        for i in range(simulate_time):
            print(i)
            # expansion
            node = self.tree_rule()
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
    selected_node.print_board()
    return 

main()
                              
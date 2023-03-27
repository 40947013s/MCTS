import sys
import json
import random
import numpy as np
import jsbeautifier
from time import time
from copy import deepcopy
from itertools import chain
from collections import defaultdict

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
        player = deepcopy(self.main_player)
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
        current_node = self
        if len(current_node.unpassed_actions) == 0:
            return None
        action = current_node.unpassed_actions.pop()
        moved_board = current_node.move(color=self.color, source=action[:2], dest=action[2:])

        # 關注!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        player = deepcopy(current_node.main_player)
        if current_node.simu_player != None:
            player = current_node.simu_player
        
        if player == 'ORDER':
            simu_player = 'CHAOS'
        else:
            simu_player = 'ORDER'
            
        child_node = MCTS_Node(board=moved_board, color_base=deepcopy(current_node.color_base), main_player=current_node.main_player, simu_player=simu_player, parent=current_node, parent_action=action)    
        current_node.children.append(child_node)
        return child_node
    
    # 遊戲是否結束
    def is_game_over(self):
        # 待改
        return True if np.count_nonzero(self.board) > 42 else False        
    
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
        b = deepcopy(self.board)
        
        player = deepcopy(self.main_player)
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
        cur = self
        while not cur.is_game_over():        
            actions = cur.get_legal_actions()
            action = cur.rollout_rule(actions)
            moved_board = cur.move(color=cur.color, source=action[:2], dest=action[2:])

            player = deepcopy(cur.main_player)   
            if cur.simu_player != None:
                player = cur.simu_player      
                      
            simu_player = 'CHAOS' if player == 'ORDER' else 'ORDER'   
            child_node = MCTS_Node(board=moved_board, color_base=deepcopy(cur.color_base), main_player=self.main_player, simu_player=simu_player, parent=cur, parent_action=action)    
            cur.children.append(child_node)            
            cur = child_node
        return cur
            
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
        game = RP(player=self.main_player, board=deepcopy(self.board))
        
        for row in range(7):
            for col in range(7):
                if game.board[row][col] == 0:
                    game.board[row][col] = game.color_base.pop()
        return game.board
    
    def game_result(self):    
        board = self.early_end() 
        score = self.get_score(board)
        if score == 80:
            return 0, 0
        if self.main_player == 'CHAOS':
            if score > 80:
                return -1, score // 7
            else:
                return 1, score // 7
        else:
            if score < 80:
                return -1, score // 7
            else:
                return 1, score // 7
        
    def backpropagate(self, result=None, point=None):
        self.visited_time += 1
        if point == None:
            result, point = self.game_result()
        self.game_results[result] += point
        if self.parent:
            self.parent.backpropagate(result, point)   
            
    def is_fully_expanded(self):
        return len(self.unpassed_actions) == 0
    
    def select(self, c=10):
        ucb_array = []
        for child in self.children:
            ucb_array.append((child.q() / child.n()) + c * np.sqrt((2 * np.log(self.n()) / child.n())))
        return self.children[np.argmax(ucb_array)]
    
    def tree_rule(self):
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
        node = None       
        for i in range(simulate_time):
            # expansion
            # print(i)
            random.shuffle(self.color_base)
            node = self.tree_rule()
            # simulation
            end = node.rollout()
            #backpropagation
            end.backpropagate()
        dfs = MCTSTreeDFS(self)
        print('start')
        with open('data.json', 'w') as f:
            f.write('[')
            dfs.traverse(self, f) 
            f.write(']')
        return self.select()
   
class MCTSTreeDFS:
    def __init__(self, root_node):
        self.root = root_node
        self.visited = set()
        self.depth = 0

    def traverse(self, node, file):
        self.visited.add(node)
        
        data = {
            "Depth": self.depth,
            "N": int(node.visited_time),
            "Wins": int(node.game_results[1]),
            "Loses": int(node.game_results[-1]),
            "Parent": str(node.parent_action),
            "board": node.board.tolist()
        }
        
        options = jsbeautifier.default_options()
        options.indent_size = 2
        json_data = jsbeautifier.beautify(json.dumps(data), options)
        if file.tell() > 1:
            # 如果檔案目前有資料，就在前面加上 ',' 符號
            file.write(',')
        file.write(json_data)
        file.write('\n')
            
        # print("  " * self.depth, end="")
        # print(f"Depth {self.depth}, N: {node.visited_time}, Q: {node.game_results}, P :{node.parent_action}, C : {len(node.children)}")
        if node.children:
            self.depth += 1
            if self.depth <= 1:                
                for child in node.children:
                    if child not in self.visited:
                        self.traverse(child, file)
            # for child in node.children:
            #     if child not in self.visited:
            #         self.traverse(child, file)
            self.depth -= 1

def main():
    start = time()
    player = 'ORDER'
    game = RP(player=player)
    root = MCTS_Node(board=game.board, main_player=player, color_base=game.color_base, color=2)
    selected_node = root.best_action(simulate_time=4500)
    selected_node.print_board()
    end = time()
    print(end-start)
    print('final', selected_node.parent_action)
    return 
        
if __debug__ == False:
    main()

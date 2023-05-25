#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tensorflow import keras
import numpy as np



# 準備 x_test 與 y_test 資料 ... [略]
name = 'mix90-97'
data=[]
with open('game_score/game_score/'+ name+'.txt',encoding='utf8') as f:
    for line in f:
      data.append(line.split())

# print(data)
# print(len(data))
score=[]
game=[]

# print(np.shape(data))
for i in range(len(data)):
  if i%9==0:
    # score.append(float(data[i][0])/540.0)
    score.append(float(data[i][0]))
  elif i%9!=8:
    for j in range(7):
      # data[i][j] = float(data[i][j])/10.0
      data[i][j] = float(data[i][j])
    game.append(data[i])

game_2d=[]
num = []
for i in range(len(game)):
  if i%7==0 and i!=0:
    game_2d.append(num)
    num = []
  num.append(game[i])

game_2d.append(num)
num = []
# print(game_2d)
# print(len(score))
# print(len(game_2d))

game_1d=[]
tmp = []
for i in range(len(game_2d)):
  for j in range(7):
    tmp.append(game_2d[i][j])
  game_1d.append(tmp)

# 計算剩餘顏色
color = [0, 0, 0, 0, 0, 0, 0]
color_list = []
for i in range(len(game_2d)):
  for j in range(7):
      for k in range(7):
        if game_2d[i][j][k]==1:
          color[0]+=1
        elif game_2d[i][j][k]==2:
          color[1]+=1
        elif game_2d[i][j][k]==3:
          color[2]+=1
        elif game_2d[i][j][k]==4:
          color[3]+=1
        elif game_2d[i][j][k]==5:
          color[4]+=1
        elif game_2d[i][j][k]==6:
          color[5]+=1
        elif game_2d[i][j][k]==7:
          color[6]+=1
  for i in range(7):
    color[i] = 7-color[i]
  color_list.append(color)
  color = [0, 0, 0, 0, 0, 0, 0]
  
# 2D盤面(數字表示他的row和col有同樣顏色的個數)
game_same_color_num = []
tmp_list = []
tmp = []
tmp2 = []
# print(game_2d[0])
for i in range(len(game_2d)):
    for j in range(7):
      for k in range(7):
        num = -1
        space = 0
        for m in range(7):
          if game_2d[i][j][m] == game_2d[i][j][k]:
            num+=1
          if game_2d[i][j][m] == 0:
            space+=1
          if game_2d[i][m][k] == game_2d[i][j][k]:
            num+=1
          if game_2d[i][m][k] == 0:
            space+=1
        # 目前盤面同色個數
        tmp.append(num)
        # 不是空格
        if game_2d[i][j][k]!=0:
            # 幾個空格
            tmp.append(space)
            tmp.append(color_list[i][int(game_2d[i][j][k])-1])
        else:
            #是空格
            tmp.append(num)
            tmp.append(0)
            
    game_same_color_num.append(tmp)
    tmp = []
# print('game_same_color_num', game_same_color_num)
# print(game_same_color_num[0])
# print(len(game_same_color_num[0]))

"""# 生成輸入"""
x_train = []
y_train = []
x_test = []
y_test = []


# game_same_color_num 一維
# 打亂訓練樣本

game_same_color_num = np.array(game_same_color_num)
score = np.array(score)
order = np.random.randint(0, len(game_same_color_num), size = len(game_same_color_num))
game_same_color_num = game_same_color_num[order]
score = score[order]

for i in range(len(game_same_color_num)):
  if i < (len(game_same_color_num)*0.8):
    x_train.append(game_same_color_num[i])
    y_train.append(score[i])
  else:
    x_test.append(game_same_color_num[i])
    y_test.append(score[i])

#改成numpy array
x_train = np.array(x_train)
y_train = np.array(y_train)
x_test = np.array(x_test)
y_test = np.array(y_test)
# 資料正規化
mean = x_train.mean(axis=0)
std = x_train.std(axis = 0) # 標準差
x_train = (x_train-mean)/std
x_test = (x_test-mean)/std

print(type(x_train))
print(type(y_train))
print(type(x_test))
print(type(y_test))

print(x_train.shape)
print(y_train.shape)
print(x_test.shape)
print(y_test.shape)
# print(y_train[0:5])
# print(y_test[0:5])
# print(x_train[0])


# 從 HDF5 檔案中載入模型
model = keras.models.load_model(name+'.h5')

# 評估模型
score = model.evaluate(x_test, y_test, verbose=0)

# 輸出結果
print('Test loss:', score[0])
print('Test accuracy:', score[1])

#測試
# test_predictions = model.predict(x_test[0], verbose = 0).flatten()
print('前十筆測試標籤', y_test[0:10])
test_predictions = model.predict(x_test[0:10], verbose = 0).flatten()
print('前十筆預測結果', np.round(test_predictions))


#!/usr/bin/env python
# coding: utf-8

# # 青少年生活调查
# #这不是源文档，原文档为 离群值检测.ipynb ，请使用jupyter notebook或vscode打开！！！
# #### 顾翔，沈贝宁、那铭心、季诚
# ---
# ## 运行环境
# * python3
# * 安装有pandas库
# * Anaconda、jupyter notebook

# ### 数据处理
# ----
# * 使用pandas的get_dummies可快速生成onehot向量，这里并没有使用
# * 将结果储存在output.csv


import pandas as pd
df = pd.read_csv('responses.csv')

#按照关键词生成onehot向量
keyword=['never smoked','tried smoking','former smoker','current smoker']
for n in range(0,4):
    one_hot=[]
    for i in range(0,int(df.shape[0])):
        if(df['Smoking'][i]==keyword[n]):
            one_hot.append(1)
        else:
            one_hot.append(0)
    df.insert(df.shape[1],keyword[n],one_hot)

#没数据的单独生成onehot向量
one_hot=[]
for i in range(0,int(df.shape[0])):
    if(pd.isnull(df['Smoking'][i])):
        one_hot.append(1)
    else:
        one_hot.append(0)
df.insert(df.shape[1],'Miss Smoking Data',one_hot)

#del df['Smoking'] 删掉原来的数据
#将结果储存到output
df.to_csv('output.csv')
df.head()


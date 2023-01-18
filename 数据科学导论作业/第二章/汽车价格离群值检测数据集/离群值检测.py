#!/usr/bin/env python
# coding: utf-8

#这不是源文档，原文档为 离群值检测.ipynb ，请使用jupyter notebook或vscode打开！！！

# # 汽车价格离群值检测
# 
# #### 顾翔，沈贝宁、那铭心、季诚
# ---
# ## 运行环境
# * python3
# * 安装有pandas、scikit-learn、numpy
# * Anaconda、jupyter notebook

# ### 一、数据处理
# * 将均相同的数据，即上市年份（2006）删除
# * 将档次、引擎缸数、换挡方式改写为onehot向量



import pandas as pd
import numpy as np

def data_processing(data):
    df = pd.read_csv(data)
    onehot_trim=[]
    for i in range(0,int(df.shape[0])):
        if(df['trim'][i]=='ex'):
            onehot_trim.append(1)
        else:
            onehot_trim.append(0)
    df.insert(df.shape[1],'onehot_trim',onehot_trim)

    onehot_engine=[]
    for i in range(0,int(df.shape[0])):
        if(df['engine'][i]=='4 Cyl'):
            onehot_engine.append(1)
        else:
            onehot_engine.append(0)
    df.insert(df.shape[1],'onehot_engine',onehot_engine)

    onehot_transmission=[]
    for i in range(0,int(df.shape[0])):
        if(df['transmission'][i]=='Automatic'):
            onehot_transmission.append(1)
        else:
            onehot_transmission.append(0)
    df.insert(df.shape[1],'onehot_transmission',onehot_transmission)
    del df['year']
    del df['trim']
    del df['engine']
    del df['transmission']
    #df.head()
    return df


# ### 二、对数据进行局部离群因子算法LOF
# * 使用了scikit-learn库：https://scikit-learn.org/stable/index.html
# * scikit-learn的LOF算法的文档地址：https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html
# * 存在的问题：
# 
#     1.只使用了价格和里程数，没有使用到档次、引擎缸数、换挡方式，而根据常识，这些因素也可能造成价格变化，因此检测出来的离群值不一定准确
#     
#     2.关于参数n_neighborsint,官方文档的解释是： default=20，Number of neighbors to use by default for kneighbors queries. If n_neighbors is larger than the number of samples provided, all samples will be used.，但实际效果邻居数量=20时得到的结果并不如人意，实测为5左右更符合预期，我认为可能是数据量太小导致的



from sklearn.neighbors import LocalOutlierFactor as LOF
def data_LOF(df):
    df_LOF=pd.DataFrame()
    df_LOF=pd.concat([df['mileage'],df['price']],axis=1)
    np_LOF=df_LOF.values
    clf=LOF(n_neighbors=5, contamination=0.1)
    y_pred=clf.fit_predict(np_LOF)
    x_scores=clf.negative_outlier_factor_
    return y_pred,x_scores,np_LOF


# ### 三、作图
# * 参考scikit-learn的官方样例：https://scikit-learn.org/stable/auto_examples/neighbors/plot_lof_outlier_detection.html#sphx-glr-auto-examples-neighbors-plot-lof-outlier-detection-py



import matplotlib.pyplot as plt
def draw(np_LOF,y_pred,x_scores,data):
    plt.scatter(np_LOF[:,0],np_LOF[:,1],color='g',s=3.,label='Data points')
    radius = (x_scores.max()-x_scores)/(x_scores.max()-x_scores.min())
    plt.scatter(np_LOF[:, 0],np_LOF[:, 1],s=1000 * radius,edgecolors='r',facecolors='none',label='Outlier scores')
    plt.axis('tight')
    plt.xlim((15000,150000))
    plt.ylim((1000,20000))
    legend = plt.legend(loc='lower right')
    plt.xlabel(data)
    legend.legendHandles[0]._sizes = [10]
    legend.legendHandles[1]._sizes = [20]
    plt.show()


# ### 四、主程序


df=data_processing('accord_sedan_testing.csv')
y_pred=data_LOF(df)[0]
x_scores=data_LOF(df)[1]
np_LOF=data_LOF(df)[2]
draw(np_LOF,y_pred,x_scores,'accord_sedan_testing.csv')

df=data_processing('accord_sedan_training.csv')
y_pred=data_LOF(df)[0]
x_scores=data_LOF(df)[1]
np_LOF=data_LOF(df)[2]
draw(np_LOF,y_pred,x_scores,'accord_sedan_training.csv')


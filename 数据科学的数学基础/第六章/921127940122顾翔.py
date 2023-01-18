#!/usr/bin/env python
# coding: utf-8

# In[5]:


import numpy as np
def forward_HMM(O,PI,A,B):
    """
    已知模型，求解状态序列概率
    :param O:  1D,观测序列（元素为整数）
    :param PI: 1D,初始概率向量
    :param A:  2D,状态转移矩阵
    :param B:  2D,观测生成矩阵
    :return:   floaat,O的概率
    """
    PI=np.asarray(PI).ravel()
    A=np.asarray(A)
    B=np.asarray(B)
    
    #求解第一步的前向概率
    alphas=B[:,O[0]]*PI
    
    #求解第二步至第T步的前向概率
    for index in O[1:]:
        alphas=np.dot(alphas,A)*B[:,index]
    
    #累计最后所有隐藏状态的前向概率
    return alphas.sum()
if __name__=='__main__':
    #初始概率向量
    PI=[0.25,0.25,0.25,0.25]
    #状态转移矩阵N*N，N个隐含状态
    A=[[0,1,0,0],[0.4,0,0.6,0],[0,0.4,0,0.6],[0,0,0.5,0.5]]
    #观测概率矩阵N*M，N个隐含状态，M个观测状态
    B=[[0.5,0.5],[0.3,0.7],[0.6,0.4],[0.8,0.2]]
    #观测序列，0代表“红”，1代表“白”
    O=[0,0,1,1,0]
    
    print(forward_HMM(O,PI,A,B))
    


# In[ ]:





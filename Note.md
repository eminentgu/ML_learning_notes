# 李宏毅2021笔记(持续更新)
## Lesson 1 中英互译
---
* regression && classification 回归与分类
* Loss : how good a set of value is
* Error Surface ：Large L ->red 
* Error Surface ：Small L->blue
* Learning rate
* Optimization 优化
* Gradient gescent 梯度下降
* parameters 参数/模型参数,由模型通过学习得到的变量，比如权重和偏置
* hyperparameters 超参数/算法参数,根据经验进行设定，影响到权重和偏置的大小，比如迭代次数、隐藏层的层数、每层神经元的个数、学习速率等
* generalization 泛化，指的是模型依据训练时采用的数据，针对以前未见过的新数据做出正确预测的能力。
* stationarity 平稳性，数据集中数据的一种属性，表示数据分布在一个或多个维度保持不变。这种维度最常见的是时间，即表明平稳性的数据不随时间而变化。例如，从 9 月到 12 月，表明平稳性的数据没有发生变化。

## Lesson 2 
---
 ![](https://img10.360buyimg.com/ddimg/jfs/t1/219306/1/2758/591809/617ff263E1289e0d4/282f597c248c5552.jpg)

## Lesson 3 when gradient is small
---
### local minima && saddle point

* critical points has two types：local minima ans saddle point(usually)
![BCD445C0-A2B3-433D-9AA2-2654E8CE4C9B.jpeg](https://img10.360buyimg.com/ddimg/jfs/t1/205875/25/13880/292850/617ff4e6E5084f109/d1f96b542397f270.jpg)
* To identify between local minima ans saddle point,use Hessian (eigen value) and it can be used to escape saddle point(not recommended)

* add data's dimension can be useful to escape saddle point

## Lessson 4 Batch and Momentum
---
* Smaller batch size and momentum help escape critical points 
### Batch

![](https://img14.360buyimg.com/ddimg/jfs/t1/218733/14/2660/442559/617ff7e9E68c01ff0/21b9a187c4cb9de5.jpg)

### Momentum (动量)
![](https://img12.360buyimg.com/ddimg/jfs/t1/215226/1/2795/402356/617ffb0aE8934cc4d/18a1489f3765f6fe.jpg)

* Monentum can be used to escape critical points efficiently

## Lesson 5 Adaptive Learning Rate
---
* 通常我们在还没到critical points的时候就会被卡住，因为固定了Lrate，当Lrate过大的时候，就会在local minima上震荡；当Lrate过小的时候，在非常平坦的地方(gradient->0)就会止步不前
* Learning Rate Schedule
![](https://img13.360buyimg.com/ddimg/jfs/t1/151207/38/25037/417583/61828b8cE54130b8f/fd62eb9173fd3763.jpg)
* 改进：Root Mean Square(Adagrad)->RMSProp->Adam
![](https://img12.360buyimg.com/ddimg/jfs/t1/156219/34/23158/238465/61828bbbEb860f9f3/6cab5a9a3c0f408c.jpg)

## Lesson 6 Batch Normalization(批标准化)
---
* 为什么需要BN
![](https://img13.360buyimg.com/ddimg/jfs/t1/169237/7/23802/451222/6183d7e5E8cc14be2/3a4429971da756aa.jpg)

    将输入数据标准化可以避免出现这样的情况
    
* 由于每一layer输出的数据也可能有较大差异，因此在输入到下一层之前也需要做BN

* BN中，$\mu$ 和 $\sigma$ 是由所有输出的数据计算得到的，因此每一个输出都会影响下一层所有的输入，即"牵一发而动全身"
* 但是，归一化(sigmod)以后，所有输入的数据会在0附近，有时候可能真实数据并不是这样的，因此加入了两个超参数来调节
![](https://img10.360buyimg.com/ddimg/jfs/t1/200478/18/15877/530767/6183daebEc1b52779/2cf56d8332898db1.jpg)
* 对于test，由于工业生产中有时得到的数据不足以构成一个batch，因此无法计算$\mu$ 和 $\sigma$，所以，选择使用以下方法来解决。
![](https://img12.360buyimg.com/ddimg/jfs/t1/220018/26/3136/211318/6183dbf8E258e2710/a90370b569649987.jpg)
* 关于BN为什么work还有部分争论

## Lesson 7 Classification
---

* classification本质还是regression
* 使用one-hot vector(独热向量)，而不是class 1;class 2;class 3是因为1,2,3会对网络产生1，2有关；1，3无关的误解，而独热向量可以避免这个问题
* 很容易改变输出的维度(regression->classification)
![](https://img13.360buyimg.com/ddimg/jfs/t1/217480/4/3158/595878/6183de9cE75729072/8c07e531e9bf9ecd.jpg)

* softmax可以将数据化为(0,1)同时放大数据之间的差距
![](https://img11.360buyimg.com/ddimg/jfs/t1/210949/36/8035/491175/6183ec13Ed33cf7e1/7002673790b3bed8.jpg)

* Loss of Classification
* 通常用Cross-entropy，而且pytorch里将其和softmax绑定在一个set里
![](https://img12.360buyimg.com/ddimg/jfs/t1/171565/37/22219/241707/6183f0b0Ecc4dc35f/e8eb66d73a9de370.jpg)

![](https://img13.360buyimg.com/ddimg/jfs/t1/135812/21/21431/573393/6183f0b0Eb8a7efdb/eb4feaf0605db34a.jpg)

## Lesson 8 CNN
---
* 常用于图像识别等，可以通过数据的部分特征来分类    
* 简化方法1：Receptive Field(感受野)-->将整张图分成小channel，每个channel守备Receptive Field做局部识别，比如，人可以通过鸟的嘴来判断这是一只鸟，cnn也是这个思路，padding可以补零也可以补别的
  ![](https://img11.360buyimg.com/ddimg/jfs/t1/207595/38/8360/269066/61868c3eEd49cff74/3227c840a50fed68.jpg)

* 不管鸟嘴在图片的哪个部分，我们依然通过相同的方式来确认图里是一只鸟，因此识别鸟嘴这个任务的channel可以共用参数来简化
  ![](https://img11.360buyimg.com/ddimg/jfs/t1/211230/23/8250/584196/61868fd0E0a295b40/30893ebd445e70a9.jpg)

* conclude 
  ![](https://img13.360buyimg.com/ddimg/jfs/t1/139780/17/26808/290401/61869571Ecfd8fd1b/46cd08d34583b58d.jpg)

* Pooling：缩小图片,Max Pooling,average pooling......
* 因为：Convolution会增加channel，因此需要Pool来把输出减小到原channel以便下一次Convolution
  
  ![](https://img13.360buyimg.com/ddimg/jfs/t1/216827/21/3471/349095/6186986eE1cb7bb67/662c3612de110e79.jpg)

* The Whole CNN
  
  ![55DEFFB5-0924-4E40-B525-7D5A8B112292.jpeg](https://img10.360buyimg.com/ddimg/jfs/t1/201489/3/14709/294348/618698acE5909dee7/5e0e0f635a4e0f88.jpg)

* Tips：Alpha Go uses CNN,but does not use Pooling......
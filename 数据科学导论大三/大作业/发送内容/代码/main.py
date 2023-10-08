#main.py是分类模型在整个测试集运行，不包含可视化、结果分析和完成报告其他部分的代码
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import accuracy_score, classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
import joblib
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False
import warnings
warnings.filterwarnings("ignore")



print("读取并处理数据！")
train_data = pd.read_csv('KDDTrain+.txt', sep=',',header= None)

train_data.columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'outcome', 'level']

train_data = train_data.dropna()
test_data = pd.read_csv('KDDTest+.txt', sep=',',header= None)
test_data.columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'outcome', 'level']

test_data = test_data.dropna()

train_data["dst_host_srv_rerror_rate"] = train_data["dst_host_srv_rerror_rate"].apply(pd.to_numeric, errors='coerce')
train_data["srv_serror_rate"] = train_data["srv_serror_rate"].apply(pd.to_numeric, errors='coerce')
train_data["rerror_rate"] = train_data["rerror_rate"].apply(pd.to_numeric, errors='coerce')
train_data = train_data.reset_index()
text_columns = train_data.select_dtypes(include=['object'])
test_data["dst_host_srv_rerror_rate"] = test_data["dst_host_srv_rerror_rate"].apply(pd.to_numeric, errors='coerce')
text_columns = test_data.select_dtypes(include=['object'])
test_data = test_data.reset_index()
train_data_text = pd.get_dummies(train_data[['protocol_type', 'service', 'flag']])
test_data_text = pd.get_dummies(test_data[['protocol_type', 'service', 'flag']])
df_zeros = pd.DataFrame(0, index=range(len(test_data_text)), columns=['service_aol', 'service_urh_i', 'service_http_2784', 'service_http_8001', 'service_harvest', 'service_red_i'])
test_data_text = pd.concat([test_data_text, df_zeros],axis = 1).reindex(columns=train_data_text.columns).reset_index()
del test_data_text["index"]




columns_used = ['duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'level']
# 初始化标准化器和归一化器
scaler = StandardScaler()
minmax_scaler = MinMaxScaler()

# 对列进行标准化
scaled_columns = scaler.fit_transform(train_data[columns_used])
train_data_standardized = pd.DataFrame(scaled_columns, columns=[columns_used])
test_data_standardized = pd.DataFrame(scaler.transform(test_data[columns_used]), columns=[columns_used])



normalized_columns = minmax_scaler.fit_transform(train_data_standardized[columns_used])
train_data_normalized = pd.DataFrame(normalized_columns, columns=[columns_used])
test_data_normalized = pd.DataFrame(minmax_scaler.transform(test_data_standardized[columns_used]), columns=[columns_used])

def process_column_value(value):
    if value == 'normal':
        return 0
    else:
        return 1


#print(train_data_normalized.shape,train_data_normalized.isna().sum().sum())
#print(train_data_text.shape,train_data_text.isna().sum().sum())
x_train = pd.concat([train_data_text,train_data_normalized],axis = 1)
#del x_train["index"]


y_train = train_data['outcome']
y_train_2 = y_train.apply(process_column_value)

x_test = pd.concat([test_data_text,test_data_normalized],axis = 1)
#del x_test["index"]
y_test = test_data['outcome']
y_test_2 = y_test.apply(process_column_value)




# 初始化 PCA 模型，并指定降维后的维度
n_components = 42 # 降维后的维度
pca = PCA(n_components=n_components)

# 将高维特征数据进行降维
x_train_pca = pca.fit_transform(x_train)
x_test_pca = pca.transform(x_test)


# 创建降维后的 DataFrame
x_train_pca = pd.DataFrame(data=x_train_pca, columns=[f'PC{i+1}' for i in range(n_components)])
x_test_pca = pd.DataFrame(data=x_test_pca, columns=[f'PC{i+1}' for i in range(n_components)])


print("数据处理完成！")
print("--------------------------------------------------------------------")
print("开始使用多层感知机二分类！")
mlp_clf = MLPClassifier(hidden_layer_sizes=(115), max_iter=100) #100
mlp_clf.fit(x_train_pca, y_train_2)
y_pred = mlp_clf.predict(x_test_pca)
accuracy = accuracy_score(y_test_2, y_pred)
print("二分类完成！")
print("Accuracy:", accuracy)
print(classification_report(y_test_2, y_pred))
print(classification_report(y_test_2, y_pred))
model_filename = "MLPClassifier_2.pkl"
joblib.dump(mlp_clf, model_filename)
print("模型保存为MLPClassifier_2.pkl")

print("--------------------------------------------------------------------")
print("开始随机森林多分类！")
y_label = pd.concat([y_test,y_train],axis = 0).reset_index()
name_list = list(y_label['outcome'].unique())
name_dict = {}
for i in range(len(name_list)):
    name_dict[name_list[i]] = i
y_train_mul = y_train_2.reindex()
y_test_mul = y_test_2.reindex()

for i in range(len(y_train)):
    y_train_mul[i] = name_dict[y_train[i]]
#print(y_train_mul)
for i in range(len(y_test)):
    y_test_mul[i] = name_dict[y_test[i]]

rf_classifier = RandomForestClassifier(n_estimators=50)
rf_classifier.fit(x_train_pca, y_train_mul)
y_pred = rf_classifier.predict(x_test_pca)
accuracy = accuracy_score(y_test_mul, y_pred)
print("多分类完成！")
print(f'Accuracy: {accuracy:.2f}')
print(classification_report(y_test_mul, y_pred))
model_filename = "RandomForestClassifier_mul.pkl"
joblib.dump(mlp_clf, model_filename)
print("模型保存为RandomForestClassifier_mul.pkl")

print("--------------------------------------------------------------------")
print("在去除训练集未出现的测试集类别后")
print("开始二分类")

train_data = pd.read_csv('KDDTrain+.txt', sep=',',header= None)

train_data.columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'outcome', 'level']

train_data = train_data.dropna()
train_data.head()
test_data = pd.read_csv('KDDTest+.txt', sep=',',header= None)
test_data.columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'outcome', 'level']

test_data = test_data.dropna()
test_data.head()


columns_set1 = set(train_data['outcome'])
columns_set2 = set(test_data['outcome'])
columns_diff1 = columns_set1 - columns_set2
columns_diff2 = columns_set2 - columns_set1
for i in list(columns_diff2):
    test_data = test_data[test_data['outcome'] != i]
test_data = test_data.reset_index()
del test_data["index"]
text_columns = train_data.select_dtypes(include=['object'])
text_columns = test_data.select_dtypes(include=['object'])
train_data["dst_host_srv_rerror_rate"] = train_data["dst_host_srv_rerror_rate"].apply(pd.to_numeric, errors='coerce')
train_data["srv_serror_rate"] = train_data["srv_serror_rate"].apply(pd.to_numeric, errors='coerce')
train_data["rerror_rate"] = train_data["rerror_rate"].apply(pd.to_numeric, errors='coerce')
train_data = train_data.reset_index()
text_columns = train_data.select_dtypes(include=['object'])
test_data["dst_host_srv_rerror_rate"] = test_data["dst_host_srv_rerror_rate"].apply(pd.to_numeric, errors='coerce')
text_columns = test_data.select_dtypes(include=['object'])
test_data = test_data.reset_index()
train_data_text = pd.get_dummies(train_data[['protocol_type', 'service', 'flag']])
test_data_text = pd.get_dummies(test_data[['protocol_type', 'service', 'flag']])
df_zeros = pd.DataFrame(0, index=range(len(test_data_text)), columns=['service_aol', 'service_urh_i', 'service_http_2784', 'service_http_8001', 'service_harvest', 'service_red_i'])
test_data_text = pd.concat([test_data_text, df_zeros],axis = 1).reindex(columns=train_data_text.columns).reset_index()
del test_data_text["index"]
columns_used = ['duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'level']
scaler = StandardScaler()
minmax_scaler = MinMaxScaler()
scaled_columns = scaler.fit_transform(train_data[columns_used])
train_data_standardized = pd.DataFrame(scaled_columns, columns=[columns_used])
test_data_standardized = pd.DataFrame(scaler.transform(test_data[columns_used]), columns=[columns_used])
normalized_columns = minmax_scaler.fit_transform(train_data_standardized[columns_used])
train_data_normalized = pd.DataFrame(normalized_columns, columns=[columns_used])
test_data_normalized = pd.DataFrame(minmax_scaler.transform(test_data_standardized[columns_used]), columns=[columns_used])
def process_column_value(value):
    if value == 'normal':
        return 0
    else:
        return 1



x_train = pd.concat([train_data_text,train_data_normalized],axis = 1)
y_train = train_data['outcome']
y_train_2 = y_train.apply(process_column_value)
x_test = pd.concat([test_data_text,test_data_normalized],axis = 1)
y_test = test_data['outcome']
y_test_2 = y_test.apply(process_column_value)
x_test[x_test.isnull() == True] = x_test[x_test.isnull() == True].fillna(0)
n_components = 42  
pca = PCA(n_components=n_components)
x_train_pca = pca.fit_transform(x_train)
x_test_pca = pca.transform(x_test)
x_train_pca = pd.DataFrame(data=x_train_pca, columns=[f'PC{i+1}' for i in range(n_components)])
x_test_pca = pd.DataFrame(data=x_test_pca, columns=[f'PC{i+1}' for i in range(n_components)])
y_label = pd.concat([y_test,y_train],axis = 0).reset_index()
name_list = list(y_label['outcome'].unique())
name_dict = {}
for i in range(len(name_list)):
    name_dict[name_list[i]] = i
#print(name_dict)
y_train_mul = y_train_2.reindex()
y_test_mul = y_test_2.reindex()

for i in range(len(y_train)):
    y_train_mul[i] = name_dict[y_train[i]]
#print(y_train_mul)
#print(y_test_2)
for i in range(len(y_test)):
    y_test_mul[i] = name_dict[y_test[i]]


mlp_clf = MLPClassifier(hidden_layer_sizes=(115), max_iter=100, random_state=42) #100
mlp_clf.fit(x_train_pca, y_train_2)
y_pred = mlp_clf.predict(x_test_pca)
accuracy = accuracy_score(y_test_2, y_pred)
print("在去除训练集没有的类别后，多层感知机二分类完成！")
print("Accuracy:", accuracy)
print(classification_report(y_test_2, y_pred))
print("--------------------------------------------------------------------")
print("在去除训练集没有的类别后，开始进行随机森林多分类")
rf_classifier = RandomForestClassifier(n_estimators=42, random_state=42)
rf_classifier.fit(x_train_pca, y_train_mul)
y_pred = rf_classifier.predict(x_test_pca)
accuracy = accuracy_score(y_test_mul, y_pred)
print("在去除训练集没有的类别后，随机森林多分类分类完成！")
print(f'Accuracy: {accuracy:.2f}')
print(classification_report(y_test_mul, y_pred))
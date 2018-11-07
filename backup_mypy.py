
# coding: utf-8

# In[86]:


import os
import shutil

root_old = r'C:\he'
root_new = r'D:\me\mypy\he_bak'

import pandas as pd
import numpy as np


# In[4]:


def up_files(path):
    '''获取文件路径与大小存入字典'''
    files_dict = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            files_dict.setdefault('path', []).append(file_path)
            files_dict.setdefault('times', []).append(os.path.getmtime(file_path))
    return files_dict


# In[5]:


def df_table(root_old, root_new):
    o = up_files(root_old)
    n = up_files(root_new)

    so = pd.DataFrame(o['times'], index=o['path'], columns=['old'])
    sn = pd.DataFrame(n)

    sn['inx'] = sn.path.apply(lambda x:x.replace(root_new, root_old))
    sn.set_index('inx', inplace=True)

    fuse = so.join(sn, how='outer')
    fuse.columns = ['old_times', 'new_path', 'new_times']
    
    return fuse


# In[75]:


def backup_files(root_old, root_new):
    
    fuse = df_table(root_old, root_new)

    '''复制新增的文件'''
    if len(fuse[fuse['new_times'].isna()]) != 0:
        com_add = fuse[fuse['new_times'].isna()].copy() # 使用copy复制，否则生成的将会是原dataframe的视图
        com_add.new_path = com_add.index.map(lambda x:x.replace(root_old, root_new)) # 成生备份目录路径

        for old, new in zip(com_add.index, com_add.new_path):

            if not os.path.isdir(os.path.split(new)[0]):    
                os.makedirs(os.path.split(new)[0])
                shutil.copy2(old, new)
                print(f'1. add file {new}')
            else:
                shutil.copy2(old, new)
                print(f'2. add file {new}')

    '''复制修改过的文件'''            
    if len(fuse[fuse['old_times'] > fuse['new_times']]) != 0:
        com_copy = fuse[fuse['old_times'] > fuse['new_times']]
        for s in zip(com_copy.index, com_copy.new_path):
            shutil.copy2(s[0], s[-1])
            print(f'copy file {s[0]}')


    '''删除多余文件'''
    if len(fuse[fuse.old_times.isna()]) != 0:
        
        # 打开删除提示
        #print('备份文件夹中存在多余文件！')
        #for unn in fuse[fuse.old_times.isna()]['new_path']:
        #    print(unn)
        #if input('是否删除文件？（Y/N）').upper() == 'Y': 
        
        
        if True:
            for unn in fuse[fuse.old_times.isna()]['new_path']:
                os.remove(unn)
                print(f'delete file {unn}')
        else:
            print('操作已取消')



if len(up_files(root_new)) == 0:
    with open(f'{root_new}\\init.txt', 'w') as f:
        f.write('init')

backup_files(root_old, root_new)
input('--')
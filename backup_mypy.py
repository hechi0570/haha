
# coding: utf-8
import os
import shutil
import pandas as pd
import numpy as np

class BakFile():
    def __init__(self, old, new):
        self.old = old
        self.new = new
        self.gen_path()        


    def gen_path(self):
        '''生成目录列表'''
        self.root_old = []
        self.root_new = []
        for dir in os.listdir(self.old):
            dir_tem  = os.path.join(self.old, dir)
            if os.path.isdir(dir_tem):
                self.root_old.append(dir_tem)
                self.root_new.append(os.path.join(self.new, dir))
                # print(dir)       

    def df_table(self):
        o = self.up_files(self.root_old)
        n = self.up_files(self.root_new)

        so = pd.DataFrame(o['times'], index=o['path'], columns=['old'])
        sn = pd.DataFrame(n)

        sn['inx'] = sn.path.apply(lambda x:x.replace(self.new, self.old))
        sn.set_index('inx', inplace=True)

        self.fuse = so.join(sn, how='outer')
        self.fuse.columns = ['old_times', 'new_path', 'new_times']
        # print(self.fuse)
        return self.fuse


    def up_files(self, paths):
        '''获取文件路径与大小存入字典'''
        files_dict = {'path': [], 'times': []}
        for path in paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    files_dict.setdefault('path', []).append(file_path)
                    files_dict.setdefault('times', []).append(os.path.getmtime(file_path))
        return files_dict


    def backup_files(self):        
        fuse = self.df_table()

        '''复制新增的文件'''
        if len(fuse[fuse['new_times'].isna()]) != 0:
            com_add = fuse[fuse['new_times'].isna()].copy() # 使用copy复制，否则生成的将会是原dataframe的视图
            com_add.new_path = com_add.index.map(lambda x:x.replace(self.old, self.new)) # 成生备份目录路径

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
                print(f'update file {s[0]}')

        '''删除多余文件'''
        if len(fuse[fuse.old_times.isna()]) != 0:  
            print(f'{"="*100}\n备份文件夹中存在多余文件！')
            for unn in fuse[fuse.old_times.isna()]['new_path']:
               print(unn)
            if input('是否删除文件？（Y/N）').upper() == 'Y':
                for unn in fuse[fuse.old_times.isna()]['new_path']:
                    os.remove(unn)
                    print(f'delete file {unn}')
                self.excess_dir()
            else:
                print('操作已取消')
    
    def excess_dir(self):
        '''处理多余的文件夹'''
        self.exc_dir = []
        new_dirs = self.fuse[bak.fuse.old_times.isna()].new_path.apply(lambda x: os.path.abspath(f'{x}\..')).unique()
        old_dirs = self.fuse[~bak.fuse.old_times.isna()].new_path.apply(lambda x: os.path.abspath(f'{x}\..')).unique() 
        
        def match_dir(new_dir, old_dirs):
            if new_dir not in old_dirs:
                self.exc_dir.append(new_dir)
                new_dir = os.path.abspath(f'{new_dir}\..') # 返回上一级目录
                # print(new_dir)
                if os.path.split(new_dir)[1] != '':
                    return match_dir(new_dir, old_dirs)
        
        for new_dir in new_dirs:
            match_dir(new_dir, old_dirs)

        for dir_P in set(self.exc_dir):
            try:        
                shutil.rmtree(dir_P)
                print(f'del dir {dir_P}')
            except FileNotFoundError:
                print(f'skip {dir_P}')
        



if __name__ == "__main__":

    old = r'C:\he'
    new = r'D:\me\mypy\he_bak' 
    bak = BakFile(old, new)
    bak.backup_files()    
    input('--')
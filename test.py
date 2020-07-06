import os

# 获取test.py文件的路径

path = os.path.dirname(os.path.abspath(__file__))
print(path)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)

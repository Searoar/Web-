"""在导入应用前使用内存库，避免污染本地 slowtravel.db。"""

import os

os.environ["SQLITE_PATH"] = ":memory:"
os.environ["API_KEY"] = "test-api-key"

# 清除可能已在其他模块加载过的 engine 缓存不可行；确保本包最先设置环境变量。
# pytest 会先于测试模块加载本文件。

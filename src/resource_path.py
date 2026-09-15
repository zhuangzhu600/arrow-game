import sys
import os


def resource_path(relative_path):
    """
    获取资源文件的绝对路径。
    开发环境：项目根目录下。
    打包后：PyInstaller 临时解压目录（sys._MEIPASS）下。
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
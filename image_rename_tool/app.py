from flask import Flask, render_template, request, jsonify
from picture import ImageRenameTool
import os
import warnings
import ctypes  # 用于获取Windows系统盘符

warnings.filterwarnings("ignore", category=UserWarning)  # 屏蔽Tkinter相关警告

app = Flask(__name__)
rename_tool = ImageRenameTool()

# 基础路径初始化为空，用于判断是否需要显示盘符列表
BASE_PATH = ""


def get_windows_drives():
    """获取Windows系统中所有可用盘符"""
    drives = []
    # 通过Windows API获取逻辑驱动器掩码
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    # 检查每个字母对应的驱动器是否存在
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if bitmask & 1:  # 如果对应位为1，表示存在该驱动器
            drive_path = f"{letter}:\\"
            if os.path.isdir(drive_path):
                drives.append(drive_path)
        bitmask >>= 1  # 右移一位检查下一个驱动器
    return drives


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/browse', methods=['POST'])
def browse_folder():
    """获取指定路径下的子文件夹列表，支持显示盘符"""
    data = request.json
    current_path = data.get('path', BASE_PATH)

    # 若当前路径为空，返回所有盘符（Windows系统）
    if not current_path:
        drives = get_windows_drives()
        folders = []
        for drive in drives:
            folders.append({
                'name': drive,  # 显示盘符如 "C:\", "D:\"
                'path': drive
            })
        return jsonify({
            'status': 'success',
            'current_path': '此电脑',  # 根目录显示为"此电脑"
            'folders': folders
        })

    # 验证路径有效性
    if not os.path.isdir(current_path):
        current_path = BASE_PATH

    try:
        # 获取所有子文件夹
        items = os.listdir(current_path)
        folders = []
        for item in items:
            item_path = os.path.join(current_path, item)
            if os.path.isdir(item_path):
                folders.append({
                    'name': item,
                    'path': item_path
                })

        # 按名称排序
        folders.sort(key=lambda x: x['name'].lower())

        # 添加上级目录
        parent_path = os.path.dirname(current_path)

        # 处理盘符根目录的上级（返回"此电脑"）
        if parent_path == current_path or current_path.endswith(':\\'):
            folders.insert(0, {
                'name': '.. (此电脑)',
                'path': ''
            })
        # 普通目录的上级
        else:
            folders.insert(0, {
                'name': '.. (上级目录)',
                'path': parent_path
            })

        return jsonify({
            'status': 'success',
            'current_path': current_path,
            'folders': folders
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'无法访问文件夹: {str(e)}'
        })


@app.route('/preview', methods=['POST'])
def preview_rename():
    """生成重命名预览"""
    data = request.form
    folder = data.get('folder_path')
    prefix = data.get('prefix', 'image')
    start_num = data.get('start_num', '1')
    num_digits = data.get('num_digits', '2')

    # 验证文件夹是否有效
    if not folder or not os.path.isdir(folder):
        return jsonify({
            'status': 'error',
            'message': '请选择有效的文件夹'
        })

    # 调用工具类生成预览
    preview, msg = rename_tool.generate_preview(folder, prefix, start_num, num_digits)
    if preview:
        return jsonify({
            'status': 'success',
            'preview': preview,
            'message': msg
        })
    else:
        return jsonify({
            'status': 'error',
            'message': msg
        })


@app.route('/rename', methods=['POST'])
def execute_rename():
    """执行重命名操作"""
    data = request.form
    folder = data.get('folder_path')
    prefix = data.get('prefix', 'image')
    start_num = data.get('start_num', '1')
    num_digits = data.get('num_digits', '2')

    # 验证文件夹是否有效
    if not folder or not os.path.isdir(folder):
        return jsonify({
            'status': 'error',
            'message': '请选择有效的文件夹'
        })

    # 执行重命名
    success, msg = rename_tool.execute_rename(folder, prefix, start_num, num_digits)
    if success:
        return jsonify({
            'status': 'success',
            'message': msg
        })
    else:
        return jsonify({
            'status': 'error',
            'message': msg
        })


if __name__ == '__main__':
    app.run(debug=True)
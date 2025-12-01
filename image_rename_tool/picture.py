import os
import re

class ImageRenameTool:
    def __init__(self):
        # 支持的图片格式
        self.image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff')
        self.status = "就绪"

    def get_image_files(self, folder):
        """获取文件夹中的图片文件"""
        if not folder or not os.path.isdir(folder):
            return [], "请选择有效的文件夹"

        try:
            files = os.listdir(folder)
            image_files = [f for f in files if f.lower().endswith(self.image_extensions)]
            image_files.sort()
            return image_files, "成功获取图片文件"
        except Exception as e:
            return [], f"无法读取文件夹: {str(e)}"

    def generate_preview(self, folder, prefix, start_num, num_digits):
        """生成重命名预览"""
        # 验证输入
        try:
            start_num = int(start_num)
            num_digits = int(num_digits)
            if start_num < 1:
                return [], "起始序号必须大于等于1"
            if num_digits < 1 or num_digits > 6:
                return [], "序号位数必须在1-6之间"
        except ValueError:
            return [], "请输入有效的数字"

        prefix = prefix.strip()
        if not prefix:
            return [], "前缀名称不能为空"

        # 获取图片文件
        image_files, msg = self.get_image_files(folder)
        if not image_files:
            return [], msg

        # 生成预览
        preview = []
        display_files = image_files[:10]
        for i, filename in enumerate(display_files, start=start_num):
            _, ext = os.path.splitext(filename)
            new_filename = f"{prefix}_{i:0{num_digits}d}{ext}"
            preview.append(f"{filename} -> {new_filename}")

        if len(image_files) > 10:
            preview.append(f"... 还有 {len(image_files) - 10} 个文件...")

        return preview, f"已预览 {len(display_files)} 个文件 (共 {len(image_files)} 个)"

    def execute_rename(self, folder, prefix, start_num, num_digits):
        """执行重命名操作"""
        # 验证输入
        try:
            start_num = int(start_num)
            num_digits = int(num_digits)
            if start_num < 1:
                return False, "起始序号必须大于等于1"
            if num_digits < 1 or num_digits > 6:
                return False, "序号位数必须在1-6之间"
        except ValueError:
            return False, "请输入有效的数字"

        prefix = prefix.strip()
        if not prefix:
            return False, "前缀名称不能为空"

        # 获取图片文件
        image_files, msg = self.get_image_files(folder)
        if not image_files:
            return False, msg

        # 执行重命名
        success_count = 0
        skip_count = 0
        error_count = 0
        error_details = []

        for i, filename in enumerate(image_files, start=start_num):
            _, ext = os.path.splitext(filename)
            new_filename = f"{prefix}_{i:0{num_digits}d}{ext}"
            old_path = os.path.join(folder, filename)
            new_path = os.path.join(folder, new_filename)

            if os.path.exists(new_path):
                skip_count += 1
                error_details.append(f"跳过: {filename} (目标文件 {new_filename} 已存在)")
                continue

            try:
                os.rename(old_path, new_path)
                success_count += 1
            except Exception as e:
                error_count += 1
                error_details.append(f"错误: {filename} - {str(e)}")

        result_msg = (f"操作完成!\n"
                      f"成功: {success_count} 个\n"
                      f"跳过: {skip_count} 个\n"
                      f"失败: {error_count} 个")

        if error_details:
            result_msg += "\n\n详细信息:\n" + "\n".join(error_details[:5])
            if len(error_details) > 5:
                result_msg += f"\n... 还有 {len(error_details) - 5} 条信息"

        return True, result_msg
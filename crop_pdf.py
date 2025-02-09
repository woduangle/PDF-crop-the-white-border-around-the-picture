import fitz
import numpy as np
import os


def crop_pdf(input_path, output_folder, zoom=4, padding=0):
    """
    裁剪PDF每一页的白边，支持长方形裁剪，输出单页PDF

    参数:
        input_path (str): 输入的PDF文件路径
        output_folder (str): 输出文件夹路径
        zoom (int): 渲染分辨率（默认4，越高越精确）
        padding (int): 内容边界扩展像素（默认0）
    """
    doc = fitz.open(input_path)

    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    for page_num, page in enumerate(doc):
        # 高精度渲染
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # 转换为numpy数组
        pixels = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)

        # 检测非白色区域（包含灰阶内容）
        non_white = np.any(pixels < 250, axis=2)  # 调低阈值包含浅色内容

        # 找到内容边界
        rows, cols = np.where(non_white)
        if len(rows) == 0 or len(cols) == 0:
            continue

        # 计算精确边界
        min_row = max(0, rows.min() - padding)
        max_row = min(pix.height, rows.max() + 1 + padding)
        min_col = max(0, cols.min() - padding)
        max_col = min(pix.width, cols.max() + 1 + padding)

        # 转换为PDF坐标（精确到小数点后2位）
        left = round(min_col / zoom, 2)
        top = round(min_row / zoom, 2)
        right = round(max_col / zoom, 2)
        bottom = round(max_row / zoom, 2)

        # 创建新PDF
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=right - left, height=bottom - top)

        # 设置裁剪区域
        crop_rect = fitz.Rect(left, top, right, bottom)
        new_page.show_pdf_page(
            fitz.Rect(0, 0, right - left, bottom - top),  # 填充整个新页面
            doc,  # 原文档
            page_num,  # 原页码
            clip=crop_rect,  # 裁剪区域
        )

        # 保存单页PDF
        output_path = os.path.join(output_folder, f"fig{page_num + 1}.pdf")
        new_doc.save(output_path)
        new_doc.close()

    doc.close()


# 使用示例
crop_pdf("1.pdf", "fig_pages")
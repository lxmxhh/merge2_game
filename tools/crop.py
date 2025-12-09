import cv2
import numpy as np
import os

def sort_contours(cnts, method="left-to-right"):
    # 初始化包围框列表
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
        key=lambda b:b[1][1], reverse=False)) # 先按Y轴（行）粗略排序

    # 简单的分行逻辑
    rows = []
    current_row = []
    if boundingBoxes:
        last_y = boundingBoxes[0][1]
        last_h = boundingBoxes[0][3]
        
        for (cnt, bbox) in zip(cnts, boundingBoxes):
            x, y, w, h = bbox
            # 如果当前物体的Y值与上一行差异超过物体高度的一半，则视为新的一行
            if y > last_y + last_h / 2:
                # 对当前行按X轴排序（从左到右）
                current_row.sort(key=lambda z: z[1][0])
                rows.extend(current_row)
                current_row = []
                last_y = y
                last_h = h
            current_row.append((cnt, bbox))
        
        # 添加最后一行
        current_row.sort(key=lambda z: z[1][0])
        rows.extend(current_row)

    return [r[0] for r in rows]

def crop_bowls(image_path):
    # 1. 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print("错误：找不到图片文件")
        return

    # 2. 预处理：转灰度 -> 二值化
    # 这一步是为了让背景变黑，物体变白，方便轮廓检测
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 因为背景是浅色的，我们用阈值处理，把浅色背景过滤掉
    # 240是一个阈值，可以根据实际情况微调
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # 3. 查找轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 4. 过滤噪点
    valid_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        # 过滤掉太小的噪点，只保留碗的大小（根据图片分辨率大概估算）
        if area > 5000: 
            valid_contours.append(c)

    # 5. 排序：确保顺序是 第一行(左->右) -> 第二行(左->右)
    sorted_cnts = sort_contours(valid_contours)

    # 6. 切割并保存
    count = 0
    # 我们只需要前6个（排除掉最后的问号，或者只取前6个）
    max_items = 14 
    
    print(f"检测到 {len(sorted_cnts)} 个物体，正在输出前 {max_items} 个...")

    for i, c in enumerate(sorted_cnts):
        if count >= max_items:
            break
            
        # 获取包围框
        x, y, w, h = cv2.boundingRect(c)
        
        # 稍微向外扩一点点边距，防止切太紧
        padding = 5
        x = max(0, x - padding)
        y = max(0, y - padding)
        w += padding * 2
        h += padding * 2
        
        # 切割
        crop = img[y:y+h, x:x+w]
        
        # 保存为PNG，保留透明通道（如果原图有）或单纯保存为高质量PNG
        output_name = f'rice_{count + 1}.png'
        cv2.imwrite(output_name, crop)
        print(f"已保存: {output_name}")
        
        count += 1

if __name__ == "__main__":
    # 请确保文件名与你上传的一致
    crop_bowls('source_pic/source3.png')
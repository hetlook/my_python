# -*- coding:utf-8 -*-
# 图像处理类
# author :wang

# class ImageUtils:
#     def __init__(self):
#         pass
#     def 
import os
import re
import openpyxl
from PIL import Image

class ImageSystem:
    """图像管理类"""
    def __init__(self):
        pass
    def get_image_info(self, filename):
        wb = openpyxl.load_workbook(os.path.join(filename, 'test.xlsx'))
        sheet_name = 'imageinfo'
        wb.create_sheet(sheet_name)
        sh = wb[sheet_name]
        sh['A1'] = 'name'
        sh['B1'] = 'size'
        re_filename = re.compile('(.*jpg$)|(.*png$)|(.*bmp$)') 
        for root, dirs, files in os.walk(filename):
            index = 2
            for name in files:
                file = os.path.join(root, name)
                if re_filename.match(file):
                    file_size = os.path.getsize(file) // 1024
                    file_size = str(file_size) + 'k'
                    print(name ,file_size)
                    sh['A' + str(index)] = name
                    sh['B' + str(index)] = file_size
                    index += 1
        wb.save(os.path.join(filename, 'test.xlsx'))
        print('excel保存完成')

    def image_rotate(self, from_name, angle, to_name, mirroring=False):
        """对图像进行旋转
            from_name : 需要旋转的图片名称
            angle : 旋转角度 镜面旋转时90为水平，180为上下 
            to_name : 旋转之后的名字
            mirroring : 是否为镜面
        """
        im = Image.open(from_name)
        if mirroring:
            if angle == 90:
                im.transpose(Image.FLIP_LEFT_RIGHT).save(to_name)
            elif angle == 180:
                im.transpose(Image.FLIP_TOP_BOTTOM).save(to_name)
        else:
            im.rotate(angle).save(to_name)
        print('保存完成！')

    def image_cutter(self, from_name, box , to_name):
        """对图像进行裁剪
            from_name : 需要旋转的图片名称
            box : 剪切的大小
            to_name : 旋转之后的名字
        """
        im = Image.open(from_name)
        region = im.crop(box)
        region.save(to_name)
        print('保存成功！')

def main():

    filename = r'C:\PythonLearn\code\module-3\work2\image_ctrl'
    image = ImageSystem()
    image.get_image_info(filename)
    image.image_rotate('C:\PythonLearn\code\module-3\work2\lulu.jpg', 180, 'C:\PythonLearn\code\module-3\work2\lulu180.jpg', mirroring=True)
    image.image_cutter('C:\PythonLearn\code\module-3\work2\lulu.jpg', (100, 100, 400, 400), 'C:\PythonLearn\code\module-3\work2\lulucut.jpg')

if __name__ == '__main__':
    main()
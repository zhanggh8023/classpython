"""
# -------------------------------
# @Time    : 2021/4/14 9:35
# @Author  : zgh
# @Email   : 849080458@qq.com
# @File    : imageMaker.py
# -------------------------------
"""
# import os
# from PIL import Image, ImageFont, ImageDraw
# import pandas as pd
# import random

# df = pd.read_csv('../fonts/lengzhishi.csv', encoding='gbk')
# num = random.randint(0, 1648)
# text = df['content'][num]
# print(num, text)
# # text = str(pd.read_csv(r'../fonts/output.csv', encoding='gbk'))
# # text = np.loadtxt(path,dtype='str',skiprows=1)
# im = Image.new("RGB", (1600, 900), (255, 255, 255))
# dr = ImageDraw.Draw(im)
# font = ImageFont.truetype(os.path.join("../fonts", "胡晓波骚包体.ttf"), 50)
# dr.text((150, 450), text, font=font, fill="#000000")
# im.show()
# im.save(r'../fonts/output.png')


from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import random
from conf import Allpath


class ImgText:

    def __init__(self, text, size):
        # 预设宽度 可以修改成你需要的图片宽度
        self.width = 1200
        # 文本
        self.text = text
        self.size = size
        # 段落 , 行数, 行高
        self.duanluo, self.note_height, self.line_height = self.split_text()

    def get_duanluo(self, text, size):
        font = ImageFont.truetype(Allpath.project_path + "/fonts/胡晓波骚包体.ttf", size)
        txt = Image.new('RGBA', (1600, 800), (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        # 所有文字的段落
        duanluo = ""
        # 宽度总和
        sum_width = 0
        # 几行
        line_count = 1
        # 行高
        line_height = 0
        for char in text:
            width, height = draw.textsize(char, font)
            sum_width += width
            if sum_width > self.width:  # 超过预设宽度就修改段落 以及当前行数
                line_count += 1
                sum_width = 0
                duanluo += '\n'
            duanluo += char
            line_height = max(height, line_height)
        if not duanluo.endswith('\n'):
            duanluo += '\n'
        return duanluo, line_height, line_count

    def split_text(self):
        # 按规定宽度分组
        max_line_height, total_lines = 0, 0
        allText = []
        for text in self.text.split('\n'):
            duanluo, line_height, line_count = self.get_duanluo(text, self.size)
            max_line_height = max(line_height, max_line_height)
            total_lines += line_count
            allText.append((duanluo, line_count))
        line_height = max_line_height
        total_height = total_lines * line_height
        return allText, total_height, line_height

    def draw_text(self, i, ii, x, y):
        """
        绘图以及文字
        :return:
        """
        font = ImageFont.truetype(Allpath.project_path + "/fonts/胡晓波骚包体.ttf", self.size)
        note_img = Image.open(i).convert("RGBA")
        draw = ImageDraw.Draw(note_img)
        # 左上角开始
        # x, y = 200, 300
        for duanluo, line_count in self.duanluo:
            draw.text((x, y), duanluo, fill="#000000", font=font)
            y += self.line_height * line_count
        note_img.save(ii)


def img_my():
    df = pd.read_csv(Allpath.project_path + '/fonts/lengzhishi.csv', encoding='gbk')
    num = random.randint(0, 1638)
    text = df['content'][num]
    print(num, text)
    ImgText(text, 50).draw_text(i=Allpath.project_path + "/fonts/output.png",
                                ii=Allpath.project_path + "/fonts/image/" + str(num) + ".png", x=200, y=200)
    ImgText("我有一条冷知识", 80).draw_text(i=Allpath.project_path + "/fonts/image/" + str(num) + ".png",
                                     ii=Allpath.project_path + "/fonts/image_zgh/" + str(num) + "_zgh.png", x=20, y=30)
    ImgText("《冷豆网》", 80).draw_text(i=Allpath.project_path + "/fonts/image_zgh/" + str(num) + "_zgh.png",
                                   ii=Allpath.project_path + "/fonts/image_zgh/" + str(num) + "_zgh.png", x=1000, y=700)
    return num


if __name__ == '__main__':
    img_my()

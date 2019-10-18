import csv
import re
import jieba
import jieba.analyse

"""
TODO:
- 添加异常处理
- 完善注释
- 添加日志
- 抽象成一个类
"""

def get_all_text(filename):
    """取出所有评价的句子
    """
    comment_list = []
    with open(filename) as f:
        rows = csv.reader(f)
        for row in rows:
            one_comment = row[1]
            comment_list.append(one_comment)

    return ''.join(comment_list[1:]) 


def cut_text(all_text):
    """找到评价中重要关键词
    """
    # https://github.com/fxsjy/jieba
    jieba.analyse.set_stop_words('stop_words.txt')
    text_tags = jieba.analyse.extract_tags(all_text, topK=30)
    return text_tags


def get_bad_words(text_tags, all_text):
    """根据关键词找到对应的句子
    """
    words = {}
    for tag in text_tags:
        tag_re = re.compile(f'(\w*{tag}\w*)')
        # print(tag_re.findall(all_text))
        words[tag] = tag_re.findall(all_text)
    return words


def main():
    all_text = get_all_text('camera.csv')
    # print(all_text)
    text_tags = cut_text(all_text)
    # print(text_tags)
    words = get_bad_words(text_tags, all_text)
    for k, v in words.items():
        print(k, '-->', len(v), v)

if __name__ == '__main__':
    main()
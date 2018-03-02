# html_str = None

with open('./weixin_history.html', 'r', encoding='utf-8') as html:
    html_str = html.read()


def extract_data(html_content):
    """
    从html页面中提取历史文章数据
    :param html_content 页面源代码
    :return: 历史文章列表
    """

    import re
    import html
    import json

    rex = "msgList = '({.*?})'"
    patten = re.compile(pattern=rex, flags=re.S)
    match = patten.search(html_content)
    if match:
        data = match.group(1)
        data = html.unescape(data)
        data = json.loads(data)
        article = data.get('list')

        for item in article:
            print(item)

        return article

import html

def sub_dict(d, keys):
    return {k: html.unescape(d[k]) for k in d if k in keys}


def get_no_of_instances(cls_obj):
    return cls_obj.__class__.no_inst

class Kls(object):
    no_inst = 0
    def __init__(self):
        Kls.no_inst = Kls.no_inst + 1

    def aa(self):
        print(self.no_inst)

def ac(*args, **kwargs):
    print(args)
    print(kwargs)

a = 'asdf:dfasdf'
k, v = a.split(':')
print(k, v)
# if __name__ == '__main__':
#     cc = {'a': 'sfasd', 'b': 'sdfasf', 'c': 'dfadsf'}
#     print(sub_dict(cc, ['a', 'b']))
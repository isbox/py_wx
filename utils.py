import html

def str_to_dict(headers):
    """
    将字符串
    Host: mp.weixin.qq.com
    Connection: keep-alive
    Cache-Control: max-age=

    转成字典对象
    {
        "Host": "mp.weixin.qq.com",
        "Connection": "keep-alive",
        "Cache-Control":"max-age="
    }

    :param headers: str
    :return: dict
    """
    headers = headers.split('\n')
    d_header = dict()
    for h in headers:
        if h.strip():
            k, v = h.split(':', 1)
            d_header[k.strip()] = v.strip()

    return d_header

def sub_dict(data, keys):
    return {da: html.unescape(data[da]) for da in data if da in keys}
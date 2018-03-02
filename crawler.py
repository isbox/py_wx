# -*- coding: utf-8 -*-
__author__ = 'xyg'

import logging
import time
import utils
import requests
import html
import json
from datetime import datetime
from urllib.parse import urlsplit
from moduls import Post

requests.packages.urllib3.disable_warnings()        # 去除ssl警告
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cookie = 'sd_userid=97161517578459991; sd_cookie_crttime=1517578459991; _ga=GA1.2.162132663.1518692855; pac_uid=0_5a8569f6e2fe5; pgv_info=ssid=s5015581103; pgv_pvid=6910448200; rewardsn=; wxtokenkey=2353955c1f0f6e5fee3b5eb39237e2a98d1645c911fe7efd7e1bf683aa25c9f3; wxuin=967558782; devicetype=android-22; version=26060339; lang=zh_CN; pass_ticket=zTKHNEdnkkZnPKGrHZa9HSJG+Ffcj38wC8ciLpAWzMsVRX2crPclnU2gSLX6h1EX; wap_sid2=CP6Mr80DElxJV3JqN3lzYlhUZkxFdVVOTkoxTXlJSzA3ZDI3R1NwMEZ0bVdFdjk5ejRXaTllSmxURjZNRm1CUEFnQmtKZUdERXdna3pjZGU1bFBuYkZqSVAtVi14YklEQUFBfjCjtOTUBTgNQAE='
appmsg_token = '946_fUMkpYbO7Txahjrps3uR7W0P3DWJ14B70CUenWQhnFavqeVp5PnD9w-O1SfW221ZLkgP5lkvkAZkYa6U'

url = 'https://mp.weixin.qq.com/mp/profile_ext' \
      '?action=home' \
      '&__biz=MjM5MzgyODQxMQ==' \
      '&scene=124' \
      '&devicetype=android-22' \
      '&version=26060339' \
      '&lang=zh_CN' \
      '&nettype=WIFI' \
      '&a8scene=3' \
      '&pass_ticket=VZC1pRCRV3PUX5VGvGbrRzij%2FCtri74EhspXkpVAAbswVrl49PjrV9ZJE9g8HLR5' \
      '&wx_header=1'

headers_str = '''
    Host: mp.weixin.qq.com
    Accept-Encoding: gzip, deflate
    Cookie: {cookie}
    Connection: keep-alive
    Accept: */*
    User-Agent: Mozilla/5.0 (Linux; Android 5.1.1; SM801 Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/043906 Mobile Safari/537.36 MicroMessenger/6.6.3.1260(0x26060339) NetType/WIFI Language/zh_CN
    Referer: https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MjM5MzgyODQxMQ==&scene=124&devicetype=iOS10.3.3&version=16060022&lang=zh_CN&nettype=WIFI&a8scene=3&fontScale=100&pass_ticket=25llsA6zWUPC9KHOvP4oE%2BQwJ3nS%2F3CjeWxeKBjDhxCb7V1lQQJa6d0ZrgSmCvWa&wx_header=1
    Accept-Language: zh-CN,en-US;q=0.8
    X-Requested-With: XMLHttpRequest
    Q-UA2: QV=3&PL=ADR&PR=WX&PP=com.tencent.mm&PPVN=6.6.3&TBSVC=43603&CO=BK&COVC=043906&PB=GE&VE=GA&DE=PHONE&CHID=0&LCID=9422&MO= SM801 &RL=1080*1920&OS=5.1.1&API=22
    Q-GUID: 1cd3b3a6ff71cc42acdc78d213b788cb
    Q-Auth: 31045b957cf33acf31e40be2f3e71c5217597676a9729f1b
'''.format(cookie=cookie)

headers = utils.str_to_dict(headers_str)
print(headers)


class WexinCrawler:
    def crawl(self, offset=0):
        """
        爬取更多文章
        :return:
        """

        json_url = 'https://mp.weixin.qq.com/mp/profile_ext'
        data = {
            'action': 'getmsg'
            , '__biz': 'MjM5MzgyODQxMQ=='
            , 'f': 'json'
            , 'offset': offset
            , 'count': '10'
            , 'is_ok': '1'
            , 'scene': '124'
            , 'uin': '777'
            , 'key': '777'
            , 'pass_ticket': 'RttWAwmYABhI3a/wJM+KR3y2XOogXkT9LLaDHmwOte/PTwH7MSQ9CC5fR6CV3KeG'
            , 'wxtoken': None
            , 'appmsg_token': appmsg_token
            , 'x5': '1'
            , 'f': 'json'
        }

        response = requests.get(json_url, params=data, headers=headers, verify=False)
        result = response.json()

        print(result)

        if result.get('ret') == 0:
            msg_list = result.get('general_msg_list')
            logger.info('抓取数据: offset=%s, data=%s' % (offset, msg_list))
            self.save(msg_list)

            # 递归调用
            has_next = result.get('can_msg_continue')
            if has_next == 1:
                next_offset = result.get('next_offset')
                time.sleep(2)
                self.crawl(next_offset)
        else:
            # 错误消息
            # {"ret":-3,"errmsg":"no session","cookie_count":1}
            logger.error('无法正确获取内容，请重新获取请求参数和请求头')
            exit()

    @staticmethod
    def save(msg_list):
        msg_list = msg_list.replace('\/', '/')
        data = json.loads(msg_list)
        msg_list = data.get('list')

        for msg in msg_list:
            p_date = msg.get('comm_msg_info').get('datetime')
            msg_info = msg.get('app_msg_ext_info')
            if msg_info:
                WexinCrawler._insert(msg_info, p_date)
                multi_msg_info = msg_info.get('multi_app_msg_item_list')

                for msg_item in multi_msg_info:
                    WexinCrawler._insert(msg_item, p_date)
            else:
                logger.warning(u'此消息不是图文推送, data=%s' % json.dumps(msg.get('comm_msg_info')))

    @staticmethod
    def _insert(item, p_date):
        keys = ['title', 'author', 'content_url', 'digest', 'cover', 'source_url']
        sub_data = utils.sub_dict(item, keys)
        post = Post(**sub_data)
        p_date = datetime.fromtimestamp(p_date)
        post['p_date'] = p_date
        logger.info('save data %s' % post.title)

        try:
            post.save()
        except Exception as e:
            logger.error('保存失败 data=%s' % post.to_json(), exc_info=True)

    @staticmethod
    def update_post(post):
        """
        :param post: :type: object mongodb中读取出来的一条数据
        :return:
        """
        data_url_params = {
            '__biz': 'MjM5MzgyODQxMQ=='
            , 'appmsg_type': '9'
            , 'mid': '2650367961'
            , 'sn': 'f519e5549538ac753ff8887707421df5'
            , 'idx': '1'
            , 'scene': '38'
            , 'title': post.title
            , 'ct': '1519553936'
            , 'abtest_cookie': 'AgABAAoADAAKAJmKHgCmih4AzooeAOqKHgAoix4APoseAEmLHgCNix4AoIseAKeLHgAAAA=='
            , 'devicetype': 'android-22'
            , 'version': '/mmbizwap/zh_CN/htmledition/js/appmsg/index3baf4b.js'
            , 'f': 'json'
            , 'r': '0.5196830451803642'
            , 'is_need_ad': '1'
            , 'comment_id': '1290332442'
            , 'is_need_reward': '0'
            , 'both_ad': '0'
            , 'reward_uin_count': '0'
            , 'msg_daily_idx': '1'
            , 'is_original': '0'
            , 'uin': '777'
            , 'key': '777'
            , 'pass_ticket': 'zTKHNEdnkkZnPKGrHZa9HSJG%252BFfcj38wC8ciLpAWzMsVRX2crPclnU2gSLX6h1EX'
            , 'wxtoken': '1574516728'
            , 'devicetype': 'android-22'
            , 'clientversion': '26060339'
            , 'appmsg_token': appmsg_token
            , 'x5': '1'
            , 'f': 'json'
        }

        content_params = dict()
        # url转义
        content_url = html.unescape(post.content_url)
        # 截取content_url查询参数部分
        content_url_params = urlsplit(content_url).query.split('&')
        # 更新到content_url_params
        for cup in content_url_params:
            k, v = cup.split('=', 1)
            content_params[k] = v
        data_url_params.update(content_params)

        data_url = 'https://mp.weixin.qq.com/mp/getappmsgext'
        headers = '''
            Host: mp.weixin.qq.com
            Connection: keep-alive
            Content-Length: 143
            Origin: https://mp.weixin.qq.com
            X-Requested-With: XMLHttpRequest
            User-Agent: Mozilla/5.0 (Linux; Android 5.1.1; SM801 Build/LMY47V; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/043909 Mobile Safari/537.36 MicroMessenger/6.6.3.1260(0x26060339) NetType/WIFI Language/zh_CN
            Content-Type: application/x-www-form-urlencoded; charset=UTF-8
            Accept: */*
            Referer: https://mp.weixin.qq.com/s?__biz=MjM5MzgyODQxMQ==&mid=2650367961&idx=1&sn=f519e5549538ac753ff8887707421df5&chksm=be9cdc8d89eb559b396a5cb61a25844a1da42c8e65ef225683c91d0f94cc2de507099ca25ec4&scene=38&ascene=0&devicetype=android-22&version=26060339&nettype=WIFI&abtest_cookie=AgABAAoADAAKAJmKHgCmih4AzooeAOqKHgAoix4APoseAEmLHgCNix4AoIseAKeLHgAAAA%3D%3D&lang=zh_CN&pass_ticket=zTKHNEdnkkZnPKGrHZa9HSJG%2BFfcj38wC8ciLpAWzMsVRX2crPclnU2gSLX6h1EX&wx_header=1
            Accept-Encoding: gzip, deflate
            Accept-Language: zh-CN,en-US;q=0.8
            Cookie: {cookie}
            Q-UA2: QV=3&PL=ADR&PR=WX&PP=com.tencent.mm&PPVN=6.6.3&TBSVC=43603&CO=BK&COVC=043909&PB=GE&VE=GA&DE=PHONE&CHID=0&LCID=9422&MO= SM801 &RL=1080*1920&OS=5.1.1&API=22
            Q-GUID: 1cd3b3a6ff71cc42acdc78d213b788cb
            Q-Auth: 31045b957cf33acf31e40be2f3e71c5217597676a9729f1b
        '''.format(cookie=cookie)
        headers = utils.str_to_dict(headers)

        # 藏在返回的text中
        body = {
            'is_only_read': '1'
            , 'req_id': '0414'
            , 'NBNjylwrVHDydtl3ufse': None
            , 'pass_ticket': 'zpU4AwNXTGS5LfBXFx4NCyMo5YTpSQo9RarrPG3tjhmMaGfORzykNNviX7IlM4i0'
            , 'is_temp_url': 0
        }


        r = requests.post(data_url, data=data_url_params, params=body, headers=headers, verify=False)
        result = r.json()

        if result.get('appmsgstat'):
            print(result.get('appmsgstat'))
            post['read_num'] = result.get("appmsgstat").get("read_num")
            post['like_num'] = result.get("appmsgstat").get("like_num")
            post['reward_num'] = result.get("reward_total_count")
            post['u_date'] = datetime.now()

            logger.info("「%s」read_num: %s like_num: %s reward_num: %s"
                        % (post.title, post['read_num'], post['like_num'], post['reward_num']))
            post.save()

        else:
            logger.error(u"没有获取的真实数据，请检查请求参数是否正确，返回的数据为：data=%s" % r.text)
            exit()

if __name__ == '__main__':
    crawler = WexinCrawler()
    # crawler.crawl()
    for post in Post.objects():
        crawler.update_post(post)
        time.sleep(2)
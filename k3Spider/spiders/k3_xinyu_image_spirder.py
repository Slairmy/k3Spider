import re
from typing import Any, Iterable

import scrapy
from loguru import logger
from scrapy import Request
from scrapy.http import Response

from k3Spider.items import K3XinyuShoeMetaData

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "www.k3.cn",
    "Referer": "https://www.k3.cn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
}

COOKIES = {
    "acw_tc": "0a47314f17399566013212893e003db007a663c5f2b4531512e91afebc5b48",
    "user_phash": "31ee09b23c016453491264206e52abe7",
    "k3cn": "dXNlcl9pZD0zODUyNTg1JnR5cGU9MCZ1c2VybmFtZT0xNzI3OTgyMTg0MUBrMy5jbiZ0PTE3Mzk5NTY2MzQmaGFzaD02NjRjODA3ZjljMTFlNmZmNWJiYWE3NDZjYWNmMTM5ZA%3D%3D",
    "daily_login": "1",
    "user_user_id": "3852585",
    "user_login_time": "2025-02-19+17%3A17%3A14",
    "user_login_ip": "14.17.101.11",
    "user_username": "17279821841%40k3.cn",
    "user_type": "0",
    "user_is_user_login": "1",
    "user_login_type": "passport",
    "user_hash": "5e633476f52313b6f0175ae400ab2fca",
}

XINYU_HOST = "http://xinyu.k3.cn"


# 爬取详情页的数据
def parse_detail(response: Response, **kwargs: Any) -> Any:
    print(f"开始解析页面: {response.url}")

    contact_div = response.css('div.business div.site_right')
    # 提取地址（排除 <b> 标签）
    address = contact_div.xpath('.//div[contains(., "拿货点")]//text()[not(parent::b)]').getall()
    address = ''.join(address).strip()  # 合并文本并去除空白字符
    address = re.sub(r'^[：\s ]+', '', address)  # 剔除开头的 `：`、空格和 ` `

    # 提取 QQ 号码（排除 <b> 标签）
    qq_number = contact_div.xpath('.//div[contains(., "Q Q")]//text()[not(parent::b)]').getall()
    qq_number = ''.join(qq_number).strip()  # 合并文本并去除空白字符
    qq_number = re.sub(r'^[：\s ]+', '', qq_number)  # 剔除开头的 `：`、空格和 ` `

    shoe_meta_data = response.meta['meta_data']
    shoe_meta_data['address'] = address or ''  # 防止 None 值
    shoe_meta_data['qq_number'] = qq_number or ''

    print("Yielding item:", dict(shoe_meta_data))
    target_user_id = response.css('div.isHideContact::attr(data-user_id)').get()
    print('目标user_id:', target_user_id)

    yield scrapy.FormRequest(
        url="https://www.k3.cn/ajax/supplier/get_contact_info",
        formdata={
            "user_id": target_user_id
        },
        cookies=response.request.cookies,
        dont_filter=True,
        meta={'meta_data': shoe_meta_data},
        callback=parse_contact,
    )


# 请求接口获取手机号码和微信
def parse_contact(response: Response, **kwargs: Any) -> Any:
    shoe_meta_data = response.meta['meta_data']
    try:
        import json
        result = json.loads(response.body)
        if result['code'] == 0:
            data = result['data']
            shoe_meta_data['mobile'] = data.get('mobile', '')
            shoe_meta_data['wx'] = data.get('wx', '')

    except Exception as e:
        logger.debug(f'获取联系方式失败:{str(e)}')

    yield shoe_meta_data


class K3XinyuImageSpider(scrapy.Spider):
    name = 'k3_xinyu_spider'
    allowed_domains = ['xinyu.k3.cn', 'www.k3.cn']
    start_urls = ['http://xinyu.k3.cn/']
    current_page = 1

    def parse(self, response: Response, **kwargs: Any) -> Any:
        li_lists = response.css('body div.container ul.content li')
        temp_lists = li_lists[:1]

        for item in temp_lists:
            shoe_meta_data = K3XinyuShoeMetaData()
            image_url = item.css('a.pictureTags img.indexImage::attr(data-url)').get()

            # 确保所有字段都有初始值
            shoe_meta_data['image_url'] = image_url or ''  # 防止 None 值
            shoe_meta_data['address'] = ''
            shoe_meta_data['qq_number'] = ''

            # 详情页面链接,需要进去爬取相关数据
            detail_page = item.css('a.pictureTags::attr(href)').get()
            if detail_page:
                yield response.follow(detail_page, cookies=COOKIES, callback=parse_detail,
                                      meta={'meta_data': shoe_meta_data})

        # 下一页
        next_page = response.css('span.next a::attr(href)').get()
        logger.debug(f'下一页: {next_page}')
        if next_page:
            if self.current_page > 3:
                return
            next_page = XINYU_HOST + next_page
            self.current_page += 1
            yield response.follow(next_page, callback=self.parse)

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# 这里定义的是一组json结构,保存需要爬取的字段信息
# 暂时先保存title和链接
class K3XinyuImageItem(scrapy.Item):
    image_url = scrapy.Field()
    title = scrapy.Field()
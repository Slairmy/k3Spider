# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class K3XinyuShoeMetaDataPipeline:

    def process_item(self, item, spider):
        print('管道处理数据,向量化图片写入向量数据库')
        print(item)

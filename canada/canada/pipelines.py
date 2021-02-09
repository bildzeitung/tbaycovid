# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


def aircode(item):
    return item.split('(')[-1][:-1]

class CanadaPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'YQT' in adapter.get('depart') or 'YQT' in adapter.get('dest'):
            fragment = f"{aircode(adapter['flight'])} from {aircode(adapter['depart'])} to {aircode(adapter['dest'])} on {adapter['date']}, rows {adapter['rows']}"
            return {"fragment": fragment}
        raise DropItem("Not relevant")

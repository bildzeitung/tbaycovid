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

    '''
    def close_spider(self, spider):
        # 4 flights per tweet
        
        #print(self._item_cache)
        #print([len(x) for x in self._item_cache])
        #print(sum(len(x) for x in self._item_cache))
        def chunks():
            for i in range(0, len(self._item_cache), self._chunks):
                yield self._item_cache[i:i+self._chunks]

        all_chunks = [c for c in chunks()]
        l = len(all_chunks)
        for x, c in enumerate(all_chunks):
            f = '\n'.join(c)
            s = f"[{x+1}/{l}] Flights with potential COVID exposure:\n{f}\n@TBDHealthUnit  @CityThunderBay"
            print(s)
            print(len(s))
    '''
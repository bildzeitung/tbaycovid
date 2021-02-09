import scrapy


class TravelSpider(scrapy.Spider):
    name = 'travel'
    allowed_domains = ['https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection/latest-travel-health-advice/exposure-flights-cruise-ships-mass-gatherings.html']
    start_urls = ['https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection/latest-travel-health-advice/exposure-flights-cruise-ships-mass-gatherings.html/']

    def parse(self, response):
        self.log(f"Got {response.headers}")

        fields = ['airline', 'flight', 'depart', 'dest', 'date', 'rows']
        for r in response.css('.mwstransform tbody tr'):
            d = [x.get().strip() for x in r.css('td::text')]
            if len(d) < len(fields):
                self.logger.warn(f"Bad line: {r.get()}")
                continue
            yield dict(zip(fields, d))

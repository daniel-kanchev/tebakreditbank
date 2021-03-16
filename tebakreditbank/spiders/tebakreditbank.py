import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from tebakreditbank.items import Article


class TebakreditbankSpider(scrapy.Spider):
    name = 'tebakreditbank'
    start_urls = ['https://www.teba-kreditbank.de/ueber-teba/']

    def parse(self, response):
        articles = response.xpath('//div[@id="collapse-82"]//div[@class="ce-bodytext"]')
        for article in articles:
            link = article.xpath('.//p/a/@href').get()
            date = article.xpath('.//time/text()').get()
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="maincontent"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

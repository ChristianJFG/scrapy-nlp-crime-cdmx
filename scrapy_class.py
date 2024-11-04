import scrapy
from scrapy.crawler import CrawlerProcess


class laprensa_spider(scrapy.Spider):
    name = "laprensa_spider"

    def __init__(self, pages, news_list):
        self.pages = pages
        self.news_list = news_list

    def start_requests(self):
        urls = self.pages
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links = response.xpath('//h4[@class="title "]/a/@href').extract()
        for link in links:
            yield response.follow(url=link, callback=self.parse2)

    def parse2(self, response):
        # Extract the title and text
        title = response.css("h1.title::text").extract_first().strip()
        text = response.xpath('//div[contains(@id,"content-body")]/p//text()').extract()
        # Join the text
        text = " ".join(text).strip()
        # Construct the new and clean
        article = title + ": " + text
        article = article.strip()
        article = article.replace("\n", " ")

        article = article.replace("\r", " ")
        article = article.replace("\t", " ")

        article = article(text)
        article = article.rstrip(
            "Síguenos en Facebook:  La Prensa Oficial  y en Twitter:  @laprensaoem"
        )
        article = article.strip()
        # date
        date = response.xpath('//p[@class="published-date"]/text()').extract_first()
        date = date.lstrip("\n\xa0 / ")
        date = date.rstrip("\n")
        new_dictionary = {"url": response.url, "date": date, "article": article}
        self.news_list.append(new_dictionary)


# Initializing parameters
pages = []
for i in range(2):
    page = (
        "https://www.la-prensa.com.mx/barebone/wf.template/config.default.master.withoutgroupcount?q=alcald%C3%ADa&section=2403&page="
        + str(i + 1)
        + "&contentType=story&sort=lastmodifieddate&order=DESC"
    )
    pages.append(page)

news_list = []
# Run the spider
process = CrawlerProcess()
process.crawl(laprensa_spider, pages=pages, news_list=news_list)
process.start()

# Save the data in a json file
import json

with open("data.json", "w") as file:
    json.dump(news_list, file)

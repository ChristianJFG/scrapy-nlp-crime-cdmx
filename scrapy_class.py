import scrapy

# Import crawler process
from scrapy.crawler import CrawlerProcess
import re
from unidecode import unidecode
import csv


class laprensa_spider(scrapy.Spider):
    name = "laprensa_spider"
    global news_list

    @staticmethod
    def clean_text(text):
        text = text.strip()

        text = text.replace("\n", " ")
        text = text.replace("\t", " ")
        text = text.replace("\r", " ")
        text = "".join(c if c == "ñ" else unidecode(c) for c in text)
        text = re.sub(
            r"Siguenos en Facebook:  La Prensa Oficial  y en Twitter:  @laprensaoem.*?$",
            "",
            text,
        )

        text = text.strip()
        regex = r"Policiaca\s+[A-Za-z¡¿\"]+.+?\s{3,}"
        text = re.sub(regex, " ", text)

        text = re.sub(r"\s+", " ", text).strip()
        text = text.lower()
        return text

    headers = ["url", "date", "article"]
    with open("text_data.csv", mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

    def start_requests(self):
        urls = pages
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

        article = laprensa_spider.clean_text(article)

        # date
        date = response.xpath('//p[@class="published-date"]/text()').extract_first()
        date = date.lstrip("\n\xa0 / ")
        date = date.rstrip("\n")

        # Saving in csv
        row = [response.url, date, article]
        with open("text_data.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)


pages = []
for i in range(100000):
    page = (
        "https://www.la-prensa.com.mx/barebone/wf.template/config.default.master.withoutgroupcount?q=alcald%C3%ADa&section=2403&page="
        + str(i + 1)
        + "&contentType=story&sort=lastmodifieddate&order=DESC"
    )
    pages.append(page)


# Run the spider
process = CrawlerProcess()
process.crawl(laprensa_spider)
process.start()

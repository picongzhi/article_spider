# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader

from article_spider.items import JobBoleArticleItem, ArticleItemLoader
from article_spider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 1.获取文章列表页中的文章url并交给Scrapy下载后进行解析
        post_nodes = response.css('div#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            image_url = post_node.css('img::attr(src)').extract_first('')
            post_url = post_node.css('::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url, post_url),
                          callback=self.parse_detail,
                          meta={'front_image_url': image_url},
                          headers={'referer': 'http://blog.jobbole.com/'})

        # 2.获取下一页的url并交给Scrapy进行下载，下载完成后交给parse函数
        next_url = response.css('.next.page-numbers::attr(href)').extract_first()
        if next_url:
            yield Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        # # 提取文章的具体字段
        # # 通过xpath提取字段
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first('')
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first('').replace('·', '').strip()
        # praise_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract_first('')
        # fav_matched = re.match(r'.*(\d+).*',
        #                        response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract_first(''))
        # if fav_matched:
        #     fav_nums = int(fav_matched.group(1))
        # else:
        #     fav_nums = 0
        # comment_matched = re.match(r'.*(\d+).*',
        #                            response.xpath('//a[@href="#article-comment"]/span/text()').extract_first(''))
        # if comment_matched:
        #     comment_nums = int(comment_matched.group(1))
        # else:
        #     comment_nums = 0
        # content = response.xpath('//div[@class="entry"]').extract_first()
        # tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        # tags = ','.join(tag_list)
        # # 文章封面图url
        # front_image_url = response.meta.get('front_image_url', '')
        #
        # article_item = JobBoleArticleItem()
        # article_item['url'] = response.url
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['title'] = title
        # try:
        #     create_date = datetime.datetime.strptime(create_date, '%Y/%m/%d').date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # article_item['create_date'] = create_date
        # article_item['front_image_url'] = [front_image_url]
        # article_item['praise_nums'] = praise_nums
        # article_item['comment_nums'] = comment_nums
        # article_item['fav_nums'] = fav_nums
        # article_item['tags'] = tags
        # article_item['content'] = content

        front_image_url = response.meta.get('front_image_url', '')
        # 通过item loader加载item
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('create_date', 'p.entry-meta-hide-on-mobile::text')
        item_loader.add_value('front_image_url', [front_image_url])
        item_loader.add_css('praise_nums', '.vote-post-up h10::text')
        item_loader.add_css('fav_nums', 'span.bookmark-btn::text')
        item_loader.add_css('comment_nums', 'a[href="#article-comment"] span::text')
        item_loader.add_css('content', 'div.entry')
        item_loader.add_css('tags', 'p.entry-meta-hide-on-mobile a::text')

        article_item = item_loader.load_item()

        yield article_item

        # 通过css选择器提取字段
        # title = response.css('.entry-header h1::text').extract()[0]
        # create_date = response.css('p.entry-meta-hide-on-mobile::text').extract()[0].strip().replace('·', '').strip()
        # praise_nums = response.css('.vote-post-up h10::text').extract()[0]
        # fav_matched = re.match(r'.*?(\d+).*',
        #                        response.css('span.bookmark-btn::text').extract()[0])
        # if fav_matched:
        #     fav_nums = fav_matched.group(1)
        # comment_matched = re.match(r'.*?(\d+).*',
        #                            response.css('a[href="#article-comment"] span::text').extract()[0])
        # if comment_matched:
        #     comment_nums = comment_matched.group(1)
        # content = response.css('div.entry').extract()[0]
        # tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        # tags = ','.join(tag_list)

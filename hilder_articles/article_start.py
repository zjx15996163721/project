from article_list_page.crawler_list_page_url import CrawlerArticleListUrl
from article_detail.crawler_article_detail import CrawlerDetail
from article_img.replace_consumer import CleanUp
from multiprocessing import Process

if __name__ == '__main__':
    produce = CrawlerArticleListUrl()
    detail_consume = CrawlerDetail()
    clean_consume = CleanUp()
    Process(target=produce.crawler_url).start()
    Process(target=detail_consume.start_consume).start()
    Process(target=clean_consume.start_consume).start()
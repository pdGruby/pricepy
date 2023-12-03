from prefect import flow, task

from crawler.crawler_otodom import CrawlerOTODOM
from crawler.crawler_olx import CrawlerOLX


@task(name='scrape_otodom_data', log_prints=True)
def scrape_otodom_data():
    crawler = CrawlerOTODOM()
    try:
        crawler.scrape()
    except Exception as e:
        crawler.kill_webdriver_processes()
        raise e
    else:
        crawler.kill_webdriver_processes()


@task(name='scrape_olx_data', log_prints=True)
def scrape_olx_data():
    crawler = CrawlerOLX()
    try:
        crawler.scrape()
    except Exception as e:
        crawler.kill_webdriver_processes()
        raise e
    else:
        crawler.kill_webdriver_processes()


@flow(name='run_crawlers', retries=3, log_prints=True)
def run_crawlers():
    scrape_olx_data()
    scrape_otodom_data()


if __name__ == "__main__":
    run_crawlers.serve(name="2023-11-29", cron='0 18,6 * * *')

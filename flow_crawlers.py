from prefect.context import FlowRunContext
from prefect import flow, task

from crawler.crawler_otodom import CrawlerOTODOM
from crawler.crawler_olx import CrawlerOLX
from crawler.data_cleaner.data_cleaner import DataCleaner


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


@task(name='clean_data', log_prints=True)
def clean_data():
    flow_name = FlowRunContext.get().flow_run.dict().get('name')

    print(f'The flow name is: {flow_name}')
    cleaner = DataCleaner(flow_name=flow_name)
    cleaner.clean_and_save_data()


@flow(name='run_crawlers', retries=3, log_prints=True)
def run_crawlers():
    scrape_olx_data()
    scrape_otodom_data()
    clean_data()


if __name__ == "__main__":
    run_crawlers.serve(name="2023-12-05", cron='0 18,6 * * *')

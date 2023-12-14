from prefect import flow, task

from app.opportunities_finder import OpportunityFinder
from _common.email_sender.flow_finished_template import send_finish_message


finder = OpportunityFinder()


@task(name='get_data', log_prints=True)
def get_data():
    finder.get_data()


@task(name='find_opportunities', log_prints=True)
def find_opportunities():
    finder.find_opportunities()


@task(name='save_opportunities', log_prints=True)
def save_opportunities():
    finder.save_opportunities()


@flow(name='find_opportunities', log_prints=True, on_completion=[send_finish_message], on_failure=[send_finish_message])
def find_opportunities():
    get_data()
    find_opportunities()
    save_opportunities()


if __name__ == "__main__":
    find_opportunities.serve(name="2023-12-14", cron='0 10 * * *')

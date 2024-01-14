from prefect import flow, task

from app.opportunities_finder import OpportunityFinder
from _common.email_sender.send_finish_message import send_finish_message


@task(name='find_and_save_opportunities', log_prints=True)
def find_and_save_opportunities():
    finder = OpportunityFinder()
    finder.get_data()
    finder.find_opportunities()
    finder.save_opportunities()


@flow(
    name='find_opportunities', log_prints=True,
    on_completion=[send_finish_message], on_failure=[send_finish_message]
)
def find_opportunities():
    find_and_save_opportunities()


if __name__ == "__main__":
    find_opportunities.serve(name="2023-12-14", cron='0 10 * * *')

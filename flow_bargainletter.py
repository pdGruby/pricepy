from prefect import flow, task

from app.bargainletter import Bargainletter
from _common.email_sender.send_finish_message import send_finish_message


@task(name='send_bargains', log_prints=True)
def send_bargains():
    bargainletter_obj = Bargainletter()
    bargainletter_obj.send_bargains()


@flow(name='bargainletter', log_prints=True, on_completion=[send_finish_message], on_failure=[send_finish_message])
def bargainletter():
    send_bargains()


if __name__ == "__main__":
    bargainletter.serve(name="2024-01-06", cron='0 11 * * *')

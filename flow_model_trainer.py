from prefect import flow, task

from ml_model.pricepy_model import PricepyModel
from _common.email_sender.flow_finished_template import send_finish_message


model = PricepyModel()


@task(name='train_model', log_prints=True)
def train_model():
    model.train_model()


@task(name='save_model', log_prints=True)
def save_model():
    model.save_model()


@flow(name='model_trainer', log_prints=True, on_completion=[send_finish_message], on_failure=[send_finish_message])
def model_trainer():
    train_model()
    save_model()


if __name__ == "__main__":
    model_trainer.serve(name="2023-12-14", cron='0 10 * * *')

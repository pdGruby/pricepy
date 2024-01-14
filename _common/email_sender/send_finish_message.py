import pytz

from _common.email_sender.email_sender import EmailSender


def send_finish_message(flow, flow_run, state):
    with open('_common/email_sender/flow_finished_template.html', 'r', encoding='utf-8') as file:
        html_template = file.read()

    cet = pytz.timezone('Europe/Warsaw')
    start_time = flow_run.start_time.replace(tzinfo=pytz.utc).astimezone(cet).strftime("%Y-%m-%d %H:%M:%S")
    flow_name = flow.name
    prefect_message = state.message
    flow_result = state.type

    values = {'flow_name': flow_name,
              'start_time': start_time,
              'flow_result': flow_result,
              'prefect_message': prefect_message}
    html_formatted = html_template.format(**values)

    sender = EmailSender(subject=f"[{flow_result}] pricepy -> {flow_name} flow finished.")
    sender.create_body(html_formatted)
    sender.send()

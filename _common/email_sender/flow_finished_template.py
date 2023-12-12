import pytz

from _common.email_sender.email_sender import EmailSender

html_template = """
<html>
<head>
    <style>
        table {{
            width: 400px;
            margin: left;
            border-collapse: collapse;
        }}

        th, td {{
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }}

        th {{
            font-weight: bold;
            background-color: #29D2F3;
        }}

        td.flow-name {{
            font-weight: bold;
            background-color: #B0E9F4;
        }}
    </style>
</head>
<body>

<p><b>|<u>  FLOW RUN DETAILS  </u>|</b></p>

<table>
    <tr>
        <th>FLOW NAME</th>
        <th>START TIME</th>
        <th>RESULT</th>
    </tr>
    <tr>
        <td class=flow-name>{flow_name}</td>
        <td>{start_time}</td>
        <td>{flow_result}</td>
    </tr>
</table>

<p><b>Message</b>: {prefect_message}</p>

</body>
</html>
"""


def send_finish_message(flow, flow_run, state):
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

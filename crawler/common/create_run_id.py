from datetime import datetime


def create_run_id(flow_name):
    return datetime.today().strftime('%Y-%m-%d') + '_' + flow_name

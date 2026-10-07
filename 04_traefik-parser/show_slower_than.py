from utils import from_seconds_to_microseconds, from_microseconds_to_seconds

def show_slower_than(log, value, show_path):
    value_in_microseconds = from_seconds_to_microseconds(value)
    if log["Duration"] > value_in_microseconds:
        print(f"FROM {log['ClientHost']} TO {log['RequestAddr']}{log['RequestPath'] if show_path else ''} BY METHOD {log["RequestMethod"]} IN {from_microseconds_to_seconds(log["Duration"])}s {log["DownstreamStatus"]}")
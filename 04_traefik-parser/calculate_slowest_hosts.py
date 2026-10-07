def calculate_slowest_hosts(log, my_dict):
    host = log["RequestAddr"]
    duration = log["Duration"]

    if host in my_dict:
        my_dict[host]["sum"] += duration
        my_dict[host]["count"] += 1
    else:
        my_dict[host] = {"sum": duration, "count": 1}
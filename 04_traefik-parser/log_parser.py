import json


def log_parser(log):

    try:
        entry = json.loads(log)

        return {
            "RequestMethod": entry["RequestMethod"],
            "ClientHost": entry["ClientHost"],
            "RequestScheme": entry["RequestScheme"],
            "RequestPath": entry["RequestPath"],
            "time": entry["time"],
            "level": entry["level"],
            "RequestAddr": entry["RequestAddr"],
            "OriginStatus": entry["OriginStatus"],
            "RequestHost": entry["RequestHost"],
            "DownstreamStatus": entry["DownstreamStatus"],
            "DownstreamContentSize": entry["DownstreamContentSize"],
            "Duration": entry["Duration"],
            "ServiceName": entry["ServiceName"]
        }
    except Exception as e:
        return None

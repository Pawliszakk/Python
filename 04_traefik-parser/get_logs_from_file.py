
def get_logs_from_file(file_path, max_lines=None):

    all_logs = []
    try:
        with open(file_path,'r') as f:
            container_logs = f.read().strip("b'\"").encode().decode("unicode_escape").splitlines()
            all_logs.extend(container_logs)

    except Exception as e:
        print("Something went wrong with parsing logs from file...")
        print(e)

    #FIX WILL BE WHEN FIX FOR STREAMING COME OUT
    if max_lines is not None:
        all_logs = all_logs[-max_lines:]

    return all_logs

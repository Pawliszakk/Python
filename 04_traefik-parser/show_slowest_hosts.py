from utils import from_microseconds_to_seconds
import csv

def show_slowest_hosts(my_dict,is_csv=False,output_path=None):

    columns = ["host","value_in_seconds"]


    def average_request_time(item):
        return item[1]["sum"] / item[1]["count"]

    sorted_request_times = sorted(my_dict.items(), key=average_request_time, reverse=True)

    if is_csv:
        output_file = f"{output_path}/slowest_hosts.csv"

        with open(output_file,'w', newline="") as f:
            writer = csv.DictWriter(f,fieldnames=columns)
            writer.writeheader()
        
            for entry in sorted_request_times:
                avg = average_request_time(entry)
                avg_in_seconds = from_microseconds_to_seconds(int(avg))

                writer.writerow({
                    columns[0]: entry[0],
                    columns[1]: avg_in_seconds
                })
        print(f"The file was saved in this path: {output_file}")
        print("\n")

    else:
        for item in sorted_request_times:
            avg = average_request_time(item)
            avg_in_seconds = from_microseconds_to_seconds(int(avg))
            print(f'{item[0]} {avg_in_seconds}s')
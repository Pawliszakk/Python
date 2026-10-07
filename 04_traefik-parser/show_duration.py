from utils import from_microseconds_to_seconds
import statistics
import csv

def show_duration(my_data,is_csv=False,output_path=None):

    sorted_all_durations_values = sorted(my_data, reverse=True)
    if len(sorted_all_durations_values) == 0:
        print("We did not find any data for specified host.")
        return    
    average_duration = sum(sorted_all_durations_values)/len(sorted_all_durations_values)

    average_duration_in_seconds = from_microseconds_to_seconds(average_duration)
    
    duration_median = from_microseconds_to_seconds(statistics.median(sorted_all_durations_values))
    
    percentyle = statistics.quantiles(sorted_all_durations_values, n=100)
    p50 = from_microseconds_to_seconds(percentyle[49])
    p95 = from_microseconds_to_seconds(percentyle[94])
    p99 = from_microseconds_to_seconds(percentyle[98])

    if is_csv:
        columns = ["avg_request_duration_value","request_median_value","p99","p95","p50","based_on_durations_value"]   
        output_file = f"{output_path}/request_statistics.csv"

        with open(output_file,'w', newline="") as f:
            writer = csv.DictWriter(f,fieldnames=columns)
            writer.writeheader()
        
            writer.writerow({
                columns[0]: round(average_duration_in_seconds,3),
                columns[1]: duration_median,
                columns[2]: p99,
                columns[3]: p95,
                columns[4]: p50,
                columns[5]: len(sorted_all_durations_values),
            })
        print(f"The file was saved in this path: {output_file}")
        print("\n")
    else:
        print('Statistics of request speed')
        print('-----------------------')

        
        print(f"Average Request duration value: {round(average_duration_in_seconds,3)}s based on {len(sorted_all_durations_values)} requests")
        print(f'Request Median Value: {duration_median}s')
        print(f'Percentyles values: ')
        print(f'Requests P99 value: {p99}s')
        print(f'Requests P95 value: {p95}s')
        print(f'Requests P50 value: {p50}s')
        print("\n")

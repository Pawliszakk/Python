import csv

def save_logs_to_csv(logs,output_path,results_number,output_name):

    columns = ["log"]
    output_file = f"{output_path}/{output_name}.csv"


    if len(logs) > 0:
        with open(output_file,'w', newline="") as f:
            writer = csv.DictWriter(f,fieldnames=columns)
            writer.writeheader()
        
            for i,log in enumerate(logs,start=1):
                if i <= results_number:
                    writer.writerow({
                        columns[0]: log,
                    })
    else:
        print("We found no data that met this requirements.")
    print(f"The file was saved in this path: {output_file}")
    print("\n")
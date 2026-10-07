import csv 
def generate_csv(dict_items, results_number,output_path, output_name):

    columns = ["name","value"]
    output_file = f"{output_path}/{output_name}.csv"


    def get_second_value(item):
        return item[1]
    if len(dict_items.items()) > 0:
        sorted_dict_items = sorted(dict_items.items(), key=get_second_value, reverse=True)
        
        with open(output_file,'w', newline="") as f:
            writer = csv.DictWriter(f,fieldnames=columns)
            writer.writeheader()
        
            for i,entry in enumerate(sorted_dict_items, start=1):
                if i <= results_number:
                    writer.writerow({
                        columns[0]: entry[0],
                        columns[1]: entry[1]
                    })
    else:
        print("We found no data that met this requirements.")
    print(f"The file was saved in this path: {output_file}")
    print("\n")
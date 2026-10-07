def show_top_metrics(message, dict_items, results_number ):
    print(message)
    print("-----------------------")
    def get_second_value(item):
        return item[1]
    if len(dict_items.items()) > 0:
        sorted_dict_items = sorted(dict_items.items(), key=get_second_value, reverse=True)
        for i,entry in enumerate(sorted_dict_items, start=1):
            if i <= results_number:
                print(f'{i}. {entry[0]:<20} | {entry[1]}')
    else:
        print("We found no data that met this requirements.")
    print("\n")
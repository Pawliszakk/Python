def count_by_occurence(log, metric, data_dict):
    my_metric = log[metric]
    my_metric_in_data_dict = data_dict.get(my_metric)

    is_my_metric_in_data_dict = bool(my_metric_in_data_dict)

    if is_my_metric_in_data_dict:
        updated_my_metric = my_metric_in_data_dict + 1
        data_dict.update(
            {my_metric: updated_my_metric}
        )
    else:
        data_dict.update({
            my_metric: 1
        })
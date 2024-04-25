import urllib.request
import urllib.parse
import json
import argparse


def merge_data(dict_1, dict_2):
    dict_3 = {**dict_1, **dict_2}
    for key, value in dict_3.items():
        if key in dict_1 and key in dict_2:
            dict_3[key] = dict_1[key] | dict_2[key]
    return dict_3


def query_prometheus_metric(prometheus_metric, timestamp, namespace, lookback):
    url = "http://prometheus.zp-ads-monitoring.k3s-dev-poc.ra-digip.net/api/v1/query?"
    params = {'time': timestamp,
              'query': f'max_over_time({prometheus_metric}'
                       '{job="kubelet", '
                       'metrics_path="/metrics/cadvisor", namespace="' + namespace + '", container!="", image!=""}'
                                                                                     f'[{lookback}])'}

    safe_params = urllib.parse.urlencode(params)
    safe_url = url + safe_params

    response = urllib.request.urlopen(safe_url)
    response_text = response.read().decode('utf-8')

    data = json.loads(response_text)

    result = {}
    for item in data['data']['result']:
        result[item['metric']['container']] = {prometheus_metric: item['value'][1]}

    return result


def query_prometheus_metrics(prometheus_metrics, parsed_args):
    return_value = {}
    for metric in prometheus_metrics:
        return_value = merge_data(return_value, query_prometheus_metric(metric, parsed_args.timestamp, parsed_args.namespace, parsed_args.lookback))
    return return_value


def convert_dictionary_to_influx_line_protocol(dictionary, repository):
    output_lines = []
    for entry in dictionary:
        output = f"self_contained_table,repository={repository},container={entry} "
        output += ",".join(f"{key}={value}" for key, value in dictionary[entry].items())
        output_lines.append(output)

    return "\n".join(output_lines)


def send_result_to_questdb(result_string):
    post_url = "http://questdb.zp-ads-monitoring.k3s-dev-poc.ra-digip.net:80/write"
    req = urllib.request.Request(post_url, data=result_string.encode())
    response = urllib.request.urlopen(req)
    print(response.read().decode('utf-8'))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timestamp', help="Timestamp representing the end of the range to query", required=True)
    parser.add_argument('-n', '--namespace', help="Namespace to query against", required=True)
    parser.add_argument('-l', '--lookback',
                        help="A prometheus time duration representing the length of the period to query", required=True)
    parser.add_argument('-r', '--repository', help="Repository where the tests being measured were run", required=True)
    parser.add_argument('-o', '--output', help="Output text file name", required=True)
    return parser.parse_args()


args = parse_arguments()

result_dict = query_prometheus_metrics(['container_memory_working_set_bytes', 'container_memory_rss'], args)
result_influx_string = convert_dictionary_to_influx_line_protocol(result_dict, "test_repo")

send_result_to_questdb(result_influx_string)
import urllib.request
import urllib.parse
import json
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-t', '--timestamp', help="Timestamp representing the end of the range to query", required=True)
parser.add_argument('-n', '--namespace', help="Namespace to query against", required=True)
parser.add_argument('-l', '--lookback', help="A prometheus time duration representing the length of the period to query", required=True)
parser.add_argument('-r', '--repository', help="Repository where the tests being measured were run", required=True)
args = parser.parse_args()

# Use the `query` endpoint and turn the instance query into a range query with `[]` syntax.
# In this example, we are reading `container_memory_working_set_bytes` starting at `time`
# and looking back 1 hour (due to the `[1h]` syntax).
#
# When running this query for real results, we would want `time` to be the instant tests end
# and the range window would be for the total length of the tests (`end_time - start_time`).
# `namespace` would be for the namespace used to run the tests being monitored.
url = "http://prometheus.zp-ads-monitoring.k3s-dev-poc.ra-digip.net/api/v1/query?"
params = {'time': args.timestamp,
          'query': 'max_over_time(container_memory_working_set_bytes{job="kubelet", '
                   'metrics_path="/metrics/cadvisor", namespace="' + args.namespace + '", container!="", image!=""}'
                   f'[{args.lookback}])'}

safe_params = urllib.parse.urlencode(params)
safe_url = url + safe_params


response = urllib.request.urlopen(safe_url)
response_text = response.read().decode('utf-8')

data = json.loads(response_text)

print("Tests were reportedly run in the " + args.repository + " repository.")

# When running for real, land data in QuestDB.
for item in data['data']['result']:
    # Displaying container name and memory usage in bytes.
    # May need additional fields so memory tracking can be linked
    # to a specific repo's tests.
    print(item['metric']['container'], item['value'][1])

# Additional queries can also be run against prometheus to capture additional memory metrics.
# Options are available here: https://github.com/google/cadvisor/blob/master/docs/storage/prometheus.md
#
# Examples I have come across call out `container_memory_rss` as something to potentially monitor
# alongside `container_memory_working_set_bytes`.
#
# We can also run a query to get the average memory usage in addition to the maximum memory usage if
# that could be useful to log.

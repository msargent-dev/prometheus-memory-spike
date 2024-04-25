# prometheus-memory-spike

## Script Using GitHub Actions Workflow

The initial prototype script queries prometheus and writes out a multi-line Influx Line Protocol file
(one table row per line). This example relies on an external call in a GitHub action workflow to actually take
the resulting file and send it to QuestDB. If you run the python script on its own, no results are sent to QuestDB.
You will only see a file as output. You can mimic the `curl` command in the example workflow file if you want to send
the example data to QuestDB.

### Help

`python workflow-script.py -h`

### Example Run

`python workflow-script.py -n zt-ateam-sys-test-01 -t 2024-04-23T17:25:59Z -l 1h -r test-repo -o output.txt`

### Testing workflow locally

Use the `act` tool to run locally.

`act -W '.github/workflows/ingest-data.yml' --container-architecture linux/amd64 -P ubuntu-latest=-self-hosted`


## Self-contained Python Script

The second prototype is a self-contained Python script that queries prometheus, formats the result, and then
sends the result off to QuestDB. If you run this script, results will end up in the database.

### Help

`python self-contained.py -h`

### Example Run

`python workflow-script.py -n zt-ateam-sys-test-01 -t 2024-04-23T17:25:59Z -l 1h -r test-repo`

### Testing workflow locally

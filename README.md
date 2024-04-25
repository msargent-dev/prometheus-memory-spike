# prometheus-memory-spike

## Help

`python main.py -h`

## Example Run

`python main.py -n zt-ateam-sys-test-01 -t 2024-04-23T17:25:59Z -l 1h -r test-repo -o output.txt`

## Testing workflow locally

Use the `act` tool to run locally.

`act -W '.github/workflows/ingest-data.yml' --container-architecture linux/amd64 -P ubuntu-latest=-self-hosted`
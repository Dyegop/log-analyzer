# Log Analyzer

A Python CLI that analyzes the content of multiple log files and saves aggregation data in a single output file.

## Prerequisites

1. [Python >=3.11][python]
2. [uv][uv]
3. [Docker (optional)][docker]

[python]: https://www.python.org/downloads/
[uv]: https://docs.astral.sh/uv/getting-started/installation/
[docker]: https://docs.docker.com/get-started/get-docker/

## Installation

Recommended: build with Docker.
```bash
git clone https://github.com/Dyegop/log-analyzer.git
cd log-analyzer

docker build -t log-analyzer .
```

Alternatively, you can install using uv lockfile in the repo:

```bash
uv sync --locked
source .venv/bin/activate
```

You can simply use pip:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install .
```

## Usage

Pass one or more input files, an output filename, and at least one operation:

```bash
log-analyzer access.log results --mfip --lfip --eps --bytes
log-analyzer first.log second.log.gz results --bytes --eps
log-analyzer access.csv results --bytes --delimiter ';'
```

For a docker run:

```bash
docker run --rm log-analyzer --help
```

Application can be run with a local input file and save results in the current directory:

```bash
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$HOME/Downloads/access.log:/inputs/access.log:ro" \
  -v "$PWD:/data" \
  log-analyzer /inputs/access.log /data/results --mfip --lfip --eps --bytes
```

The output name must not include an extension: `results` creates `results.json`.

An existing output file is replaced after the new results have been written successfully.

| Option | Calculation |
| --- | --- |
| `--mfip` | Most frequent client IPs |
| `--lfip` | Least frequent client IPs |
| `--eps` | Average events per second |
| `--bytes` | Total header and response bytes |
| `--delimiter` | CSV separator; comma by default |

Only selected operations appear in the JSON. For example:

```json
{
  "mfip": [{"ip": "192.0.2.1", "count": 2}],
  "eps": 1.5,
  "bytes": 330
}
```

## Build the package

From the repository root, run:

```bash
uv build
```

This uses the setuptools backend configured in `pyproject.toml`. Artifacts are written to `dist/`.

## Design decisions

The input contract requires each log record to follow a fixed field order. The parser identifies fields by their position, rather than inferring their meaning from their values.
Expected fields are:
```text
timestamp header_bytes client_ip status response_bytes method url username destination content_type
```

Only the `timestamp`, `client IP`, `header_bytes` and `response_bytes` are validated and used in calculations.

The tool is fault-tolerant. An invalid or malformed record is ignored, and files that cannot be opened or fully read do not break the application.

Another important is decision made is how record are analyze. The app uses lazy validation; therefore, a record with partially invalid fields is not full discarded, and only the correct fields are use for the aggregation metrics.

No usable IPs produces an empty list; no usable byte values produces zero. Empty input or no accepted records causes analysis to fail.

The app is designed for expansion; more parsers and writers can be implemented for wider file format support.

Other design decisions and assumptions made are:
* All input files contribute to one combined result.
* For optimization, records are aggregated as they are read rather than loaded into memory.
* The application currently supports input files in `.log`, `.txt` and `.csv` files.
* CSV files support multiple delimiters.
* The app supports compressed files in `gzip`.

Some future improvements the application could benefit from:
* Adding more input and output formats, including JSON input with field mapping.
* Add support for strict validation. discarding records with partially invalid fields.
* Limit decompressed input size and record length.
* Improve performance with concurrency.
* Add CI support to automate linting, tests and package builds.

## Error handling

Invalid rows are logged and skipped. Unsupported, unreadable or corrupt files are skipped, and processing continues. Records read before a file fails remain included in the result.

| Exit code | Meaning |
| --- | --- |
| `0` | Results saved with no rejected rows or failed files |
| `1` | Analysis or output failed |
| `2` | Invalid command-line arguments |
| `3` | Partial results saved after rejected rows or failed files |

Metrics count accepted records, rejected records and failed files.

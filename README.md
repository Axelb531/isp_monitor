# ISP Quality metrics

## Description
Project measuring metrics for an internet connection. Uses AWS DynamoDB for data storage.
* Measure - Contains the measurment-application (dockerized python), which could be set up as a CRON-job, for continous measurement. 
* Inspect - Contains a small dockerized dashboard plotting relevant data. 

## Installation
### Prerequisites
- Docker
- Python 3.12
- AWS account with DynamoDB access

### Setup
1. Clone the repository, and fill out the ```.env``` files according to the ````.env.template``:
```bash
git clone [repository-url] cd <repo_name>
```
2. Navigate to the cloned directory and build the Docker containers:
```bash
cd measure && docker build -t <measure_container_name>:latest .
cd ../inspect && docker build  -t <inspect_container_name>:latest .
```
## Usage - measure
Run the measurement Docker container with:
```bash
docker run --env-file <path-to-env> <measure_container_name>:latest
```
Optional flags:
- `--no-save`: Disable saving results to DynamoDB
- `--no-print`: Disable print of results

Preferably this can be set up as a cronjob using 
```bash
crontab -e
```

## Usage -inspect
Run the inspect Docker container with:
```bash
docker run --env-file <path-to-env> -h localhost -p 8080:8080 <inspect_container_name>:latest
```

## Prerequisites
- AWS account and credentials
- Docker 

## Contributing
Contributions to the project are welcome! 


## Credits
- Ookla for `speedtest-cli`

## License
This project is licensed under the MIT License - see the `LICENSE` file for details.



# Message in a bottle

## Installation

Execute the following commands:

```bash
python -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Run the application

Execute the following commands:
```bash
docker run -d -p 6379:6379 redis
./run.sh
```

To monitor Celery output:
```bash
tail -f nohup.out
```

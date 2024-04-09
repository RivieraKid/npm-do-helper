FROM python:3.11.9-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY do-npm-helper.py .

CMD ["python", "./do-npm-helper.py"]
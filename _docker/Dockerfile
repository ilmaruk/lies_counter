FROM python:3.7.3

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY lies_counter/ /src/

WORKDIR /src/

CMD ["python", "app.py"]
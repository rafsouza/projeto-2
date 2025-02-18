FROM python:3.10.5

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade -r /code/requirements.txt

COPY ./main.py /code

COPY ./ /code

# COPY ./config.py /code

# COPY ./.env /code

CMD ["python", "main.py"]
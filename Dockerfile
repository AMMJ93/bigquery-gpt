FROM python:3.11.7-bullseye

WORKDIR /app

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg 

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

RUN apt-get update && apt-get install google-cloud-cli

COPY ./app /app

RUN pip install .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
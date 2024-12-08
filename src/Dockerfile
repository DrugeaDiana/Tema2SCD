FROM python:3.6
COPY requirements.txt /tmp
RUN pip install --requirement /tmp/requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5000
CMD ["python", "server.py"]
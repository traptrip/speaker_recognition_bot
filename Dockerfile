FROM python:3.8

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y libsndfile1 ffmpeg
RUN pip install -r requirements.txt && rm requirements.txt
COPY . .

CMD ["python", "app.py"]

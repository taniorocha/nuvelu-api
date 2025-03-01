FROM python:alpine

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
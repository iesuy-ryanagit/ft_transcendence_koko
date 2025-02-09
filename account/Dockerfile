# Use official Python image
FROM python:3

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . /app/

# Expose port 8000
EXPOSE 8000

# コピーしたmigrate.shを実行可能にする
RUN chmod +x init.sh

# マイグレーションを実行する（`docker-entrypoint.sh`などを用意しても良い）
CMD ["./init.sh"]

# サーバーを起動
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# 1. Use python:3.9.16-slim as base image
FROM python:3.9.16-slim

# Set environment variables
ENV PYTHONBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

# Install necessary packages
RUN apt-get update \
    && apt-get install -y netcat

# Define the application directory
ENV APP=/app

# 2. Change the working directory to $APP
WORKDIR $APP

# 3. Copy the requirements.txt file to $APP
COPY requirements.txt $APP

# 4. Install dependencies from requirements.txt
RUN pip3 install -r requirements.txt

# 5. Copy the rest of the source code into $APP
COPY . $APP

# 6. Expose port 8000
EXPOSE 8000

# Set executable permissions for entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Define the entrypoint script
ENTRYPOINT ["/bin/bash","/app/entrypoint.sh"]

# 7. Set the default command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

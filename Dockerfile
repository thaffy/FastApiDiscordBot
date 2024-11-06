FROM python:3.9

LABEL authors="markus.hamre"

# Set the working directory
WORKDIR /code

# Copy requirements and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the app code
COPY . /code

# Set the command to run the app
CMD ["uvicorn", "app.main:app", "--port", "8000"]

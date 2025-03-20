# Set the python version as a build-time argument
ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Create a virtual environment
RUN python -m venv /opt/venv

# Set the virtual environment as the current location
ENV PATH=/opt/venv/bin:$PATH

# Upgrade pip
RUN pip install --upgrade pip

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install OS dependencies for our mini VM
RUN apt-get update && apt-get install -y \
    libpq-dev \  # for Postgres
libjpeg-dev \  # for Pillow
libcairo2 \  # for CairoSVG
netcat-traditional \  # for database check
gcc \  # other utilities
&& rm -rf /var/lib/apt/lists/*

# Create the mini VM's code directory
RUN mkdir -p /code

# Set the working directory to that same code directory
WORKDIR /code

# Copy the requirements file into the container
COPY requirements.txt /tmp/requirements.txt

# Copy the project code into the container's working directory
COPY . /code

# Install the Python project requirements
RUN pip install -r /tmp/requirements.txt

# Create static directory
RUN mkdir -p /code/static

# Collect static files (Doesn't need the database)
RUN python manage.py collectstatic --noinput

# Set the Django default project name
ARG PROJ_NAME="aibf_backend"

# Ensure database is ready before running migrations
CMD bash -c "
echo 'Waiting for database...';
while ! nc -z $PGHOST $PGPORT; do sleep 1; done;
echo 'Database is ready!';
echo 'Running migrations...';
python manage.py migrate --no-input;
echo 'Migrations completed!';
echo 'Starting Gunicorn...';
gunicorn ${PROJ_NAME}.wsgi:application --bind 0.0.0.0:8000 --log-level debug
"

# Set the python version as a build-time argument
# with Python 3.12 as the default
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

# Install os dependencies for our mini vm
RUN apt-get update && apt-get install -y \
    # for postgres
    libpq-dev \
    # for Pillow
    libjpeg-dev \
    # for CairoSVG
    libcairo2 \
    # for database check
    netcat-traditional \
    # other
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create the mini vm's code directory
RUN mkdir -p /code

# Set the working directory to that same code directory
WORKDIR /code

# Copy the requirements file into the container
COPY requirements.txt /tmp/requirements.txt

# copy the project code into the container's working directory
COPY . /code

# Install the Python project requirements
RUN pip install -r /tmp/requirements.txt

# Create static directory
RUN mkdir -p /code/static

# database isn't available during build
# run any other commands that do not need the database
# such as:
RUN python manage.py collectstatic --noinput

# set the Django default project name
ARG PROJ_NAME="aibf_backend"

# create a bash script to run the Django project
# this script will execute at runtime when
# the container starts and the database is available
RUN printf "#!/bin/bash\n" > ./paracord_runner.sh && \
    printf "set -e\n" >> ./paracord_runner.sh && \
    printf "echo \"Starting application...\"\n" >> ./paracord_runner.sh && \
    printf "echo \"Environment variables:\"\n" >> ./paracord_runner.sh && \
    printf "echo \"PGDATABASE: \$PGDATABASE\"\n" >> ./paracord_runner.sh && \
    printf "echo \"PGUSER: \$PGUSER\"\n" >> ./paracord_runner.sh && \
    printf "echo \"PGHOST: \$PGHOST\"\n" >> ./paracord_runner.sh && \
    printf "echo \"PGPORT: \$PGPORT\"\n" >> ./paracord_runner.sh && \
    printf "echo \"PORT environment variable: \$PORT\"\n" >> ./paracord_runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n\n" >> ./paracord_runner.sh && \
    printf "echo \"Resolved port: \$RUN_PORT\"\n" >> ./paracord_runner.sh && \
    printf "echo \"Waiting for database to be ready...\"\n" >> ./paracord_runner.sh && \
    printf "while ! nc -z \$PGHOST \$PGPORT; do\n" >> ./paracord_runner.sh && \
    printf "  echo \"Waiting for database at \$PGHOST:\$PGPORT...\"\n" >> ./paracord_runner.sh && \
    printf "  sleep 1\n" >> ./paracord_runner.sh && \
    printf "done\n" >> ./paracord_runner.sh && \
    printf "echo \"Database is ready!\"\n" >> ./paracord_runner.sh && \
    printf "echo \"Running migrations...\"\n" >> ./paracord_runner.sh && \
    printf "python manage.py migrate --no-input\n" >> ./paracord_runner.sh && \
    printf "echo \"Migrations completed!\"\n" >> ./paracord_runner.sh && \
    printf "gunicorn ${PROJ_NAME}.wsgi:application --bind \"0.0.0.0:\$RUN_PORT\" --log-level debug\n" >> ./paracord_runner.sh

# make the bash script executable
RUN chmod +x paracord_runner.sh

# Clean up apt cache to reduce image size
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Run the Django project via the runtime script
# when the container starts
CMD ./paracord_runner.sh    
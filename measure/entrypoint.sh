#!/bin/bash
# Entrypoint script for Docker container

# Execute the Python script with any arguments passed to the container
python /measure.py "$@"

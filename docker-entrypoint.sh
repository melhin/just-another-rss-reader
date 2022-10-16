#!/bin/bash
set -eu

for arg in "$@"
do
    case "$arg" in
        app)
            echo "Running migration"
            alembic -c alembic.ini upgrade head
            echo "Starting application"
            python run.py
            ;;
        collect)
            echo "Running migration"
            alembic -c alembic.ini upgrade head
            echo "Starting collection service"
            python collect.py
            ;;
        *)
            echo "Invalid option"
            ;;
    esac
done
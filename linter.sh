#!/bin/bash

# Function to run commands with pipenv
run_with_pipenv() {
    pipenv run flake8 kinkernel
    pipenv run black kinkernel --check --diff
    pipenv run black kinkernel
    pipenv run mypy kinkernel
    pipenv run pylint kinkernel
}

# Function to run commands without pipenv
run_without_pipenv() {
    flake8 kinkernel
    black kinkernel --check --diff
    black kinkernel
    mypy kinkernel
    pylint kinkernel
}

# Ask the user if they want to use pipenv
read -p "Do you want to use pipenv? (y/n): " use_pipenv

# Check the user input
if [[ "$use_pipenv" =~ ^[Yy]$ ]]; then
    echo "Running commands with pipenv..."
    run_with_pipenv
elif [[ "$use_pipenv" =~ ^[Nn]$ ]]; then
    echo "Running commands without pipenv..."
    run_without_pipenv
else
    echo "Invalid input. Please answer 'y' or 'n'."
    exit 1
fi

exit 0
#!/bin/bash

echo "Running Setup File"

echo "Install all dependency"
pip install -r requirement.txt &&

sleep 1

echo "Running Server"
python app.py
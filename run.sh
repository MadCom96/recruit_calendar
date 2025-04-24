#!/bin/bash

if [ "$1" == "-r" ]; then
    # reset.py 실행
    uv run reset.py
else
    # main.py 실행
    uv run main.py
fi
#!/bin/bash
token=`curl http://localhost:8000/boom/`
echo "window.token = '$token'"

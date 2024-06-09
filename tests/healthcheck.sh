#!/bin/bash

url=$1
max_retries=$2
retry_interval=$3

attempt=1
while [ $attempt -le $max_retries ]; do
    echo "Attempt $attempt: Curling $url"
    response_code=$(curl -sL -w "%{http_code}" -o /dev/null $url)

    if [ $response_code -eq 200 ]; then
        echo "Success: HTTP Status 200 received"
        exit 0
    else
        echo "Error: HTTP Status $response_code received"
        if [ $attempt -lt $max_retries ]; then
            echo "Retrying in $retry_interval seconds..."
            sleep $retry_interval
        fi
    fi

    ((attempt++))
done

echo "Maximum retries reached. Failed to receive HTTP Status 200."
exit 1
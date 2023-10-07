#!/bin/bash

output_file="memory_info.log"

while true; do
    showmem >> "$output_file"
    sleep 1
done
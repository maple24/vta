#!/system/bin/sh

output_file="/path/to/memory_info.log"  # Replace with the desired file path

while true; do
    procrank >> "$output_file"
    sleep 1
done
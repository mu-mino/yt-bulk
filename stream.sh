#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

DIR="$1"

for file in "$DIR"/*; do
    [ -f "$file" ] || continue

    echo "File: $file"

    ffprobe -v error \
        -show_entries stream=index,codec_type,codec_name,disposition:stream_tags=title \
        -of default=noprint_wrappers=1 \
        "$file"

    echo
done

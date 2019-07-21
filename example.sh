#!/usr/bin/env bash

python represent_naf.py --input_folder="example_files" \
--output_folder="output" --languages="en-it" --pos_mapping_file="example_files/pos_mapping.json" --verbose=1
python how_to_use.py
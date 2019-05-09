import csv

from glob import glob

import pandas as pd

import progressbar

filepath = "/mnt/c/Users/pierr/Downloads/cours_ml_project_datatype-master"

data = []

for filename in glob(filepath + "/*.csv"):
    print(f"Reading {filename.split('/')[-1]}...")

    # Guess delimiter
    with open(filename, 'r') as file:
        dialect = csv.Sniffer().sniff(file.read(10000))

    # Read file into pandas
    df = pd.read_csv(filename, dialect=dialect, dtype=str)

    print(f"Transforming data ({len(df.columns)} columns)...")

    # Transform data
    bar = progressbar.ProgressBar(max_value=len(df))
    for idx, row in df.iterrows():
        for col_name, elem in zip(df.columns, row):
            data.append({
                'data': elem,
                'target': col_name.split(".")[0] if col_name == col_name.lower() else 'text'
            })

        bar.update(idx)
    bar.finish()

print("Writing output...")
pd.DataFrame(data).to_csv('train.csv', index=False)

print("Finished!")
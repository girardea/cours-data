import pandas as pd

import re

datafile = "Dataset.data"
specfile = "Dataset.spec"

data_out = 'data.csv'

# Lecture des specs
with open(specfile, 'r') as file:
	# Lecture  des lignes
	lines = file.readlines()

	# Filtrage sur les noms de colonnes
	lines = [line for line in lines if '#' in line]

	# Remplaçement quand trop d'espaces
	lines = [re.sub(r'\s+', ' ', line) for line in lines if '#' in line]

	# Récupération des noms de colonnes
	cols = [line.split(' ')[2] for line in lines]

# Lecture des données
df = pd.read_csv(datafile, sep=' ', header=None, names=cols, index_col=False)

print(df.info())

print(df.sample(3).transpose())

print(df.describe().transpose())

df.to_csv(data_out, index=False)

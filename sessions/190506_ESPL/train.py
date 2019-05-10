import pandas as pd

import re

def create_X(df):
	"""Ajoute des colonnes au DF"""	
	# Pour gérer le cas du predict sur un mot.
	if type(df) == str:
		df = pd.DataFrame({
			'data': [df],
			'target': [None]
		})

	# Compte les caractères
	df['cnt'] = df['data'].apply(len)

	# Compter le nombre de chiffres
	def compte_chiffres(x):
		cnt = 0
		for char in x:
			if char in "0123456789":
				cnt += 1
		return cnt
	df['cnt_chiffres'] = df['data'].apply(compte_chiffres)

	# Compter le nombre de lettres
	def compte_lettres(x):
		return len(re.findall('[a-zA-Z]', x))
	df['cnt_lettres'] = df['data'].apply(compte_lettres)

	return df.drop(columns=['data', 'target'])

if __name__ == "__main__":
	print("Reading file...")
	df = pd.read_csv("train.csv").dropna()

	# Apprentissage
	print("Applying transforms...")
	X = create_X(df)
	y = df['target']

	from sklearn.ensemble import RandomForestClassifier

	rfc = RandomForestClassifier(n_estimators=10)

	print("Fitting classifier...")
	rfc.fit(X, y)

	# On sauve le modèle
	from joblib import dump

	print("Saving classifier...")
	dump(rfc, "rfc.joblib")

	print("Finished!")

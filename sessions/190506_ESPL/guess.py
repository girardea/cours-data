from train import create_X

from joblib import load
rfc = load("rfc.joblib")

def idiot(mot):
	return "text"

mot = input("Entrez un mot :")

print("Ce mot est de type :", idiot(mot))
intermediaire = create_X(mot)
# print(intermediaire)
print("Ce mot est de type :", rfc.predict(intermediaire))
print(f"proba :", rfc.predict_proba(intermediaire))
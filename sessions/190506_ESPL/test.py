import pandas as pd

url = "https://tinyurl.com/y4pflefj"

df = pd.read_csv(url)

print(df.info())

print(df.sample(5))

# Compter le pourcentage de cellules vides dans chaque colonne du tableau
print(df.isnull().mean())

import csv

import numpy as np

filenames = [
	"/mnt/c/Users/pierr/Downloads/data.csv",
	"/mnt/c/Users/pierr/Downloads/ademe_tc1.csv"
]

def guess_delimiter(filename):
	options = [',', ';', '\t', '|']

	delims = []

	for option in options:
		with open(filename, 'r') as f:
			occurences = [line.count(option) for line in f]

			if (np.min(occurences) > 0) and (np.min(occurences) == np.max(occurences)):
				delims.append(option)

	if not delims:
		raise Exception("No delimiter found.")
	elif len(delims) > 1:
		raise Exception("Several possibilities for delimiter:", ", ".join(delims))
	else:
		return delims[0]

for filename in filenames:
	delim = guess_delimiter(filename)

	print("guess_delimiter", filename, delim)

	# sniffer way
	with open(filename, 'r') as file:
		dialect = csv.Sniffer().sniff(file.read(), ",;\t|")
	print("sniffer", filename, dialect.delimiter)

import codecs

from csvkit import CSVKitDictReader

def csv_to_hstore(path):
	with codecs.open(path, encoding='iso-8859-1') as f:
		reader = CSVKitDictReader(f)
		for row in reader:
			print row

if __name__ == '__main__':
	import sys
	csv_to_hstore(sys.argv[1])

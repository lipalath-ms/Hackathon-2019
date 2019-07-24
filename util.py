import csv

def convert_to_tsv(fileHandle, outputFileName):
    csvReader = csv.reader(fileHandle)
    with open(outputFileName, "w", newline='') as myfile:
        wr = csv.writer(myfile, delimiter = '\t').writerows(csvReader)	

def convert_to_csv(fileHandle, outputFileName):
    csvReader = csv.reader(fileHandle, delimiter = '\t')
    with open(outputFileName, "w", newline='') as myfile:
        wr = csv.writer(myfile, delimiter = ',').writerows(csvReader)
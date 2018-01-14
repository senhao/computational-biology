import csv

## Immediate old version - 'matching_entries.py'
###Module to compare two files-Method 1 - See OLd version 'matching_entries.py'

##Module to compare two files -Method 2
#Open a file to be written in CSV format
fh_output=open('validated_out', 'w') 
csv_out=csv.writer(fh_output, delimiter=',')

fh_out_supplemental=open('validated_out_supp', 'w')
csv_out_sup=csv.writer(fh_out_supplemental, delimiter=',')


### Matching starts
validated_tuples = []

with open("PARE_valid_parsed") as fh1:
    csv_reader = csv.reader(fh1)
    for row in csv_reader:
        validated_tuples.append(tuple(row))
print('The total number of entries i.e tuples in PARE validated parsed file:', len(validated_tuples))
#print(validated_tuples[0][0:3])

with open("cleaveland_parsed") as fh2:
    csv_reader = csv.reader(fh2)
    match_count=0
    for row in csv_reader:
        if tuple(row[0:3]) in validated_tuples:
            csv_out.writerow(row[0:6])
#            entr=row[3]
#            targ=row[4]
#            miRN=row[5]
            
            csv_out_sup.writerow(row[0:6])            
#            csv_out.writerow([entr]+[targ]+[miRN])
            match_count+=1
        else:
            pass
print('\nTotal number of entries matched with validated entries:', match_count)

'''
Created on Feb 29, 2012

@author: atul
'''


'''
Created on Apr 14, 2012

@author: atul
'''

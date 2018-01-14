#!/usr/local/bin/python3

##This script is to convert tag_count files back to original expression fasta file by adding tag number of times in tag count file
##Usage : python3 tagcount2exp_v1.py <input>


import re
import sys

#inp_file_name = 'medicago.cdna'
inp_file_name   = str(sys.argv[1])
tagcount        = 'Y'   ## 'Y': If this is a tag count file or 'N' just tags
Exprs           = 'N'   ## Do you need file in expression mode i.e tag appears number of times in tag count



def Tag2FASTA(inp_file_name):
    #read file
    fh_in=open(inp_file_name, 'r')
    #write file
    out_file    = ('%s.fa' % (inp_file_name.rpartition('.')[0]))
    fh_out      = open(out_file, 'w')
    tag_num     = 1 ### For naming tags
    if tagcount == 'Y':
        if Exprs=='Y':  ### Write as raw sequencing file with tag repeated number of times it appears in tag_count 
            ##Write to file
            print('\nWriting expression file for %s tagcount file' % (inp_file_name))
            print('\n---PLEASE BE PATIENT---')
            
            for i in fh_in:##All the entries of the library
                #if len(ent[0]) == 20:
                ent     = i.strip('\n').split('\t')
                atag    = ent[0]
                acount  = int(ent[1])
                for count in range(tag_count):##Number of times the tag_count file
                    fh_out.write('>seq_%s|%s\n%s\n' % (tag_num,str(acount),atag.strip()))
                    tag_num += 1
                    
        else: ## Convert tag count to FASTA with distinct tags
            for i in fh_in:
                ent = i.strip('\n').split('\t')
                atag    = ent[0]
                acount  = int(ent[1])
                fh_out.write('>seq_%s|%s\n%s\n' % (tag_num,str(acount),atag.strip()))
                tag_num += 1
    
    else: ## Not a tagcount file - Convert to FASTA
        print ('Converting file to FASTA')
        for i in fh_in:
            fh_out.write('>Tag%s\n%s\n' % (tag_num,i.strip('\n')))
            tag_num += 1

    print('\nThe expression file %s is ready to use' % (out_file))
    fh_in.close()
    fh_out.close()
    
def main():
    Tag2FASTA(inp_file_name)
    

if __name__ == '__main__':
    main()
    sys.exit()
    

## v01 -> v02
## Added functionality to convert tagcount to FASTA
## Added functionality to convert tag to FASTA

## v02 -> v03
## Better out file name
## File name displayed in end
## Converted FASTA format conforms with phasTER


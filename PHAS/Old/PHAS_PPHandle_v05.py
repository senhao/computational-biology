#!/usr/local/bin/python3

## This script uses the phasiRNA scripts from SVN So, make sure your svn has Pingchuan phasi-prediction scripts
## Author: Atul Kakrana kakrana@udel.edu

#### FUNCTIONS ###########################################

import os,sys,subprocess,multiprocessing
import mysql.connector as sql
from multiprocessing import Process, Queue, Pool
import os.path

#### USER SETTINGS ########################################

## Genome - Mandatory
Local = 3                                           ## [0]: Files in directory [2]: Get the libs from $ALLDATA with raw reads 
                                                    ## [3] Get library from srna db with reads filtered on number of hits
geno = 'N'                                          ## Run on whole genome (Y) or transcriptome file (N) - If (N) then provide index of transcriptome
geno_index = '../index/genes.attr_table_index'           ## If geno = 'Y' then index path from $ALLDATA; if geno = 'N' then prepare index of your file 
                                                    ## using bowtie-build command like bowtie-build GENOMEFILE.fa NAME_FOR_INDEX

## sRNA - Mandatory
db = 'MAIZE_pub2_sRNA' ## sRNA DB
fetchLibIDs = 'N'                                   ## (Y): Get IDs for all libs in DB (N): If you want to run on specific libs than 'N' and specifiy libs below
userLibs = [(1746,),(1577,),(1585,),(1578,),(1586,),(1579,),(1580,),(1582,),(1583,),(1584,),(1587,),(1745,),(1735,),(1736,),(1737,),(1738,),(1739,),(1740,),(1741,),(1742,),(1743,),(1744,),(3167,),(3168,),(2851,),(2852,),(2140,),(2141,),(2142,),(2143,),(2144,),(2145,)]                ## If fetchLib = 'N' then specifiy libraru IDs in the format [(lib1,),(lib2,),(lib3,),]
phase = 21                                          ## Phase to use for prediction

## Degradome - Optional
deg = 'N'                                           ## Use Degradome validation, IF yes enter PARE db in line below
PARE = 'GuturGu'                                    ## If deg = 'Y' then File for degradome analysis

## ADVANCED SETTINGS #######################################
nproc ='Y'                                          ## Multiple processing 
server = 'raichu.dbi.udel.edu'                      ## Server to use to fetch library information and smallRNA libraries
perl = "/usr/local/bin/perl_5.18"                   ## Josh updated the perl on Tarkan and its not ready yet for PHAS script FORK is missing and somemore modules -Check with Pingchuan help

#############################################################
#############################################################

## Make mySQL connection
def ConnectToDB(server):
    
    ##infile values are '0' when you dont want to pulaod data from local file and '1' when you wish to upload data by local file
    ##EX:con=sql.connect(host= server, user='kakrana', passwd='livetheday', local_infile = infile)
    ##Now later in script you can
    ##cur.execute("LOAD DATA LOCAL INFILE './scoring_input_extend2' INTO TABLE kakrana_data.mir_page_results FIELDS TERMINATED BY ','")
    
    print ('\nTrying to connect to mySQL server on %s' % (server))
    # Try to connect to the database
    try:
        con=sql.connect(host= server, user='kakrana', passwd='livetheday')###local_infile = 1 not supported yet so a table has to be updated on row basis
        print ('Connection Established\n')

    # If we cannot connect to the database, send an error to the user and exit the program.
    except sql.Error:
        print ("Error %d: %s" % (sql.Error.args[0],sql.Error.args[1]))
        sys.exit(1)

    return con

## Get lib ids in the sRNA DB
def GetLibs(con,db):
    ##Function that gets just the list names, required to run script in parts.
    cur = con.cursor()
    cur.execute('select distinct(lib_id) from %s.library' % (db))
    libs = cur.fetchall()
    #print (libs)
    print ('\nTotal number of sRNA libraries found: %s\n' % (len(libs)))
    
    return libs###

## Deprecated
def PHASBatch(con,libs,geno,geno_index,deg):
    
    #os.mkdir('./%s' % (lib))
    #output_path = './%s' % (lib)
    
    for lib in libs:
        print (lib)
        cur = con.cursor()
        cur.execute('SELECT processed_path FROM master.library_info where lib_id = %s' % (lib))
        path = cur.fetchall()
        #print(path[0][0])
        
        pro_file = path[0][0].replace('$ALLDATA', '/alldata')###Processed sRNA file
        out_file = '%s.txt' % (lib)
        rl = str(phase)
        nproc2 = str(nproc)
        sRNAratio = str(75)
        print (pro_file)
        
        if geno == 'Y':###Uses Whole genome as input
            if deg == 'Y':
                retcode = subprocess.call([perl, "/data2/homes/kakrana/svn/users/pingchuan/phasiRNA_prediction_pipeline.ver.genome.pl", "-i", pro_file, "-q", PARE, "-f", "-t", sRNAratio, "-d", geno_index, "-px", out_file, "-rl", rl, "-cpu", nproc2])
            else:
                retcode = subprocess.call([perl, "/data2/homes/kakrana/svn/users/pingchuan/phasiRNA_prediction_pipeline.ver.genome.pl", "-i", pro_file,"-f", "-t", sRNAratio, "-d", geno_index, "-px", out_file, "-rl", rl, "-cpu", nproc2])
        
        else: ### Uses FASTA file of genes as input         
            #pipe =subprocess.Popen(["perl5.18", "-v"])
            if deg == 'Y':
                retcode = subprocess.call([perl, "/data2/homes/kakrana/svn/users/pingchuan/phasiRNA_prediction_pipeline.ver.MUL.pl", "-i", pro_file, "-q", PARE, "-f", "-t", sRNAratio, "-d", geno_index, "-px", out_file, "-rl", rl, "-cpu", nproc2])
            else:
                retcode = subprocess.call([perl, "/data2/homes/kakrana/svn/users/pingchuan/phasiRNA_prediction_pipeline.ver.MUL.pl", "-i", pro_file, "-f", "-t", sRNAratio, "-d", geno_index, "-px", out_file, "-rl", rl, "-cpu", nproc2])
                    
        
        if retcode == 0:
            pass
        else:
            print("Problem with Phasing script - Return code not 0")
            sys.exit()
        
    return lib

### sRNA Libraries are fetched from server
def TagAbundanceFile(con,db,libs):
    
        for alib in libs:##For all the libraries
            
            ## Check if file already exsits in directory - This saves a lot of time downloading the same file
            filePath = '%s' % (alib)
            if os.path.isfile(filePath) == False:
                print ('\nPreparing sRNA reads file for library: %s' % (alib[0]))
                #print (lib[0])
                #print ('Caching tag and count information from server for PARE alib %s' % (alib[0]) )
                cur = con.cursor()
                cur.execute("SELECT tag,norm from %s.run_master where lib_id = %s and hits between 1 and 20" % (db,alib[0]))
                lib_info = cur.fetchall()
                #print('These are the tags:',lib_info[:10])
                
                fh_out = open('%s' % (alib), 'w')##Naming file with lib_ids name
                print ('Library cached, writing abundance file')
                tag_num = 1
                for ent in lib_info:## All the PARE tags in a library
                    #print (ent)
                    fh_out.write('%s\t%s\n' % (ent[0],ent[1]))
                    tag_num += 1
                    
                fh_out.close()
            else:
                print('tag abundance file exists for library: %s' % (alib))
                pass

##Phasing anlysis - New
def PHASBatch2(con,libs,geno,geno_index,deg):
    for lib in libs:
        pro_file = './%s' % (lib)###Processed sRNA file
        out_file = '%s.txt' % (lib)
        
        rl = str(phase)
        nproc2 = str(nproc)
        sRNAratio = str(75)
        print (pro_file)

        if geno == 'Y':###Uses Whole genome as input
            if deg == 'Y':
                retcode = subprocess.call([perl, "/data2/homes/kakrana/svn/users/pingchuan/phasiRNA_prediction_pipeline.ver.genome.pl", "-i", pro_file, "-q", PARE, "-f", "-t", sRNAratio, "-d", geno_index, "-px", out_file, "-rl", rl, "-cpu", nproc2])
            else:
                retcode = subprocess.call([perl, "/data2/homes/kakrana/svn/users/pingchuan/phasiRNA_prediction_pipeline.ver.genome.pl", "-i", pro_file,"-f", "-t", sRNAratio, "-d", geno_index, "-px", out_file, "-rl", rl, "-cpu", nproc2])
        
        else: ### Uses FASTA file of genes as input         
            #pipe =subprocess.Popen(["perl5.18", "-v"])
            if deg == 'Y':
                retcode = subprocess.call([perl, "/data2/homes/kakrana/svn/users/pingchuan/phasiRNA_prediction_pipeline.ver.MUL.pl", "-i", pro_file, "-q", PARE, "-f", "-t", sRNAratio, "-d", geno_index, "-px", out_file, "-rl", rl, "-cpu", nproc2])
            else:
                retcode = subprocess.call([perl, "/data2/homes/kakrana/svn/users/pingchuan/phasiRNA_prediction_pipeline.ver.MUL.pl", "-i", pro_file, "-f", "-t", sRNAratio, "-d", geno_index, "-px", out_file, "-rl", rl, "-cpu", nproc2])

        if retcode == 0:
            pass
        else:
            print("Problem with Phasing script - Return code not 0")
            sys.exit()
        
    return lib

def main(server):
    con = ConnectToDB(server)
    if fetchLibIDs ==  'Y': ## Run on all libraries in the DB
        if Local == 0:
            print ("This mode expects libraries copied to present directory by user")
            print("Since you chose to 'fetchLibIDs' from smallRNA DB - Data could be fetched either from all data or DB")
            print("Please choose correct mode when fetch withLibIDs in used - Correct modes for Local:[1/2]")

        elif Local == 1: ## Get sRNA lib data from $ALLDATA
            libs = GetLibs(con,db)
            print('These are the libs: %s' % (libs))
            PHASBatch(con,libs,geno,geno_index,deg)

        else: ##Get sRNA lib data from DB of all libraries directly from DB
            libs = GetLibs(con,db)
            print('These are the libs: %s' % (libs))
            TagAbundanceFile(con,db,libs)
            PHASBatch2(con,libs,geno,geno_index,deg)
            
    else: ## Run on specific libraries

        if Local == 0: ## sRNA files in present diretcory
        	print("This mode (Local = 1) expects all smallRNA libraries in current folder")
        	print('These are the libs: %s' % (userLibs))
        	PHASBatch2(con,userLibs,geno,geno_index,deg)

        elif Local == 1: ## Get sRNA lib data of specified libraries from $ALLDATA
            print('These are the libs: %s' % (userLibs))
            PHASBatch(con,userLibs,geno,geno_index,deg)
        
        ## Get sRNA lib data of specified libraries directly from DB
        else:
        	print('These are the libs: %s' % (userLibs))
        	TagAbundanceFile(con,db,userLibs)
        	PHASBatch2(con,userLibs,geno,geno_index,deg)

if __name__ == '__main__':

    ###Processors to use####
    if nproc == 'Y':###Use default 70% of processors
        nproc = int(multiprocessing.cpu_count()*0.8)
    else:##As mannually entered by the user
        nproc == int(nproc)
    ###############
    
    main(server)
    print ('\n\nPhasing Analysis finished successfully')
    sys.exit()

### Version 01 -> v02
### Added PARE switch
### Added sRNA ratio option
### Added option to specify libs

## v02 -> v03
## Added option to get libs from the server with hits filter
## COrrected bug in main(), repaced libs with userlibs for specific librarues part
## Perl location added as variable

## v03 -> v04
## Changed order of user settings to make them more clear
## Added functionality to check if the abundance file for library already exists in folder - Saves a lot of time

## v04 -> v05
## Added local mode to run on smallRNA files specified by user and present in current directory unlike fetching from DB or ALLDATA
## Simplfied user settings

## v04->v05
## Modified the sRNA tags download module with tag hits between 1 and 20

## TO-DO
## Add automatic index resolution
## Rocket - RNA Analysis 


### Local mode

Filename fetched from sample info.txt

These are used to identify all different filetypes. In case of paired end, suffix is added to file name and used as identifiers


## Server mode 

QCheck and trimLibs reads files directly from $ALLDATA and generate processed files in local directory. These files are further used as local mode by steps starting from chopping. The identifier in this case is library id and not filename.

In case of paired end data, both QCheck and trimLibs use raw file name to generate identifiers with suffix ‘_1’ and ‘_2’. Two assumptions are made 1) paired end files are present in ALLDATA 2) and named in standard format i.e. NAME_1.fastq and NAME_2.fastq

The library information should have RAW PATH filed with NAME_1.fastq

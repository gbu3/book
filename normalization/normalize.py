"""
takes a csv (like edition_series) and splits into
seriable table + association table
can merge multiple files : 2 pairwise files +
generates one place table + 2 assoc tables 
(like for author_locations and editions_publish_places)
"""

"""
take one or more files where each row contains 
two columns as (work/edition/author, value) 
and create a normalized file for "value" 
and the association table for each of the input files.
"""

def extract_unique_values(files_to_be_normalized, keyfile):
    """
    extract the unique values for the columns to be normalized 
    and assign a sequence number for each unique value
    """

    keys = {} # for tracking the unique values and assigning a sequence number
    seq = 1
    for filename in files_to_be_normalized:
        with open(filename, 'r') as file:
            for line in file:
                columns = line.rstrip().split('\t')
                if len(columns)!=2:
                    continue
                if columns[1] not in keys:
                    keys[columns[1]] = seq
                    seq += 1

    with open(keyfile,'w') as kf:
        for k in keys:
            kf.write(f"{keys[k]}\t{k}\n")    
    return keys

def normalize(files_to_be_normalized, keys):
    for filename in files_to_be_normalized:
        columns = filename.split(".")
        if len(columns)!=2:
            continue
        filename_id = columns[0]+"_id.csv"
        with open(filename,"r") as file, open(filename_id,"w") as file_id:
             for line in file:
                columns = line.rstrip().split('\t')
                if len(columns)!=2:
                    continue
                if columns[1] in keys:
                    file_id.write(f"{columns[0]}\t{keys[columns[1]]}\n")
                else:
                    print("Missing ",columns[1],"\n",line,"\n")


unique_values = extract_unique_values(["openlib/authors_location.csv","openlib/editions_publish_places.csv"], 'testlib/places.csv')
normalize(["openlib/authors_location.csv","openlib/editions_publish_places.csv"], unique_values)

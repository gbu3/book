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

    keys = {} # track the unique values and assign a sequence number
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
    # the normalization table
    with open(keyfile,'w') as kf:
        for k in keys:
            kf.write(f"{keys[k]}\t{k}\n")    
    return keys

def normalize(files_to_be_normalized, keys):
    """
    create the csv file with the normalized data
    """
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


unique_values = extract_unique_values(["authors_location.csv","editions_publish_places.csv"], 'testlib/places.csv')
normalize(["authors_location.csv","editions_publish_places.csv"], unique_values)

unique_value = extract_unique_values(["editions_subjects","works_subjects.csv"],"subjects.csv")
normalize(["editions_subjects","works_subjects.csv"],unique_values)

unique_value = extract_unique_values(["editions_lccn.csv"],"work_titles")
normalize(["editions_lccn.csv"],unique_values)


unique_value = extract_unique_values(["authors_photos.csv"],"photos.csv")
normalize(["authors_photos.csv"],unique_values)

unique_value = extract_unique_values(["editions_contributors.csv"],"contributors.csv")
normalize(["editions_contributors.csv"],unique_values)


unique_value = extract_unique_values(["editions_genres.csv"],"genres.csv")
normalize(["editions_genres.csv"],unique_values)

unique_value = extract_unique_values(["editions_languages.csv","works_orginal_languages.csv"],"languages.csv")
normalize(["editions_languages.csv","works_orginal_languages.csv"],unique_values)

unique_value = extract_unique_values(["editions_lc_classifications.csv","works_lc_classifications.csv"],"lc_classifications.csv")
normalize(["editions_lc_classifications.csv","works_lc_classifications.csv"],unique_values)

unique_value = extract_unique_values(["editions_publishers.csv"],"publishers.csv")
normalize(["editions_publishers.csv"],unique_values)

unique_value = extract_unique_values(["editions_series.csv"],"series.csv")
normalize(["editions_series.csv"],unique_values)

unique_value = extract_unique_values(["works_dewey_number.csv"],"dewey_number.csv")
normalize(["works_dewey_number.csv"],unique_values)

unique_value = extract_unique_values(["works_other_titles.csv"],"other_titles.csv")
normalize(["works_other_titles.csv"],unique_values)

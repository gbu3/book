"""
takes a csv (like edition_series) and splits into
seriable table + association table
can merge multiple files : 2 pairwise files +
generates one place table + 2 assoc tables 
(like for author_locations and editions_publish_places)
"""

def main():
    iFiles = ["openlib/editions_subjects.csv","openlib/works_subjects.csv" ]
    kFile = "openlib/subjects.csv"

    keys = {}
    seq = 1
    for ifile in iFiles:
        with open(ifile, 'r') as file:
            for line in file:
                columns = line.rstrip().split('\t')
                if len(columns)!=2:
                    continue
                if columns[1] not in keys:
                    keys[columns[1]] = seq
                    seq += 1

    with open(kFile,'w') as kf:
        for k in keys:
            kf.write(f"{keys[k]}\t{k}\n")    

    for ifile in iFiles:
        columns = ifile.split(".")
        if len(columns)!=2:
            continue
        ifile_id = columns[0]+"_id.csv"
        with open(ifile,"r") as file, open(ifile_id,"w") as file_id:
            for line in file:
                columns = line.rstrip().split('\t')
                if len(columns)!=2:
                    continue
                if columns[1] in keys:
                    file_id.write(f"{columns[0]}\t{keys[columns[1]]}\n")
                else:
                    print("Missing ",columns[1],"\n",line,"\n")

    langs = {}
    keyfile = "openlib/publish_places.csv"
    with open(keyfile, 'r') as file:
        for line in file:
            try:
                columns = line.rstrip().split('\t')
                if len(columns<2):
                    continue
                seq = columns[0]
                lang = columns[1]
                langs[lang] = seq
            except:
                print(line)


if __name__ == '__main__':
    main()

import json

"""
takes the ol_dump and based on different fields
that are deemed necessary, generates author csvs
from the json data column for input into db
"""

def main():
    f_authors = open("openlib/authors.csv","w")
    f_photos = open("openlib/authors_photos.csv","w")
    f_location = open("openlib/authors_location.csv","w")

    with open("ol_dump_latest.txt", 'r') as file:
        round = 0
        
        for line in file:
            try:
                if "/type/author" not in line:
                    continue
        
                columns = line.split('\t')

                json_data = columns[-1].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\b',' ').replace('\x08','')
                data = json.loads(json_data)

                for k in data:
                    if isinstance(data[k], str):
                        data[k] = data[k].replace('\\t',' ').replace('\\r',' ').replace('\\n',' ')
                
                if 'type' not in data or 'key' not in data['type']:
                    continue
                    
                if data['type']['key'] != '/type/author':
                    continue

                #print(data)        
                if 'key' in data:
                    author = data['key'].split("/")[-1]
                    if author.startswith("OL"):
                        f_authors.write(f"{author}")
                    else:
                        continue
                else:
                    continue

                if 'created' in data:
                    f_authors.write(f"\t{data['created']['value']}")
                else:
                    f_authors.write(f"\t")

                if 'last_modified' in data:
                    f_authors.write(f"\t{data['last_modified']['value']}")
                else:
                    f_authors.write(f"\t")

                if 'revision' in data:
                    f_authors.write(f"\t{data['revision']}")
                else:
                    f_authors.write(f"\t")

                if 'latest_revision' in data:
                    f_authors.write(f"\t{data['latest_revision']}")
                else:
                    f_authors.write(f"\t")

                if 'name' in data:
                    title = data['name'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\x08','').replace('\uf076',' ')
                    f_authors.write(f"\t{title}")
                else:
                    f_authors.write(f"\t")
                    
                if 'fuller_name' in data:
                    title = data['fuller_name'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\x08','').replace('\uf076',' ')
                    f_authors.write(f"\t{title}")
                else:
                    f_authors.write(f"\t")
                
                if 'personal_name' in data:
                    title = data['personal_name'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\x08','').replace('\uf076',' ')
                    f_authors.write(f"\t{title}")
                else:
                    f_authors.write(f"\t")
                    
                if 'birth_date' in data:
                    f_authors.write(f"\t{data['birth_date']}")
                else:
                    f_authors.write(f"\t")
                
                if 'death_date' in data:
                    f_authors.write(f"\t{data['death_date']}")
                else:
                    f_authors.write(f"\t")
                
                if 'date' in data:
                    f_authors.write(f"\t{data['date']}")
                else:
                    f_authors.write(f"\t")
                
                if 'entity_type' in data:
                    f_authors.write(f"\t{data['entity_type']}")
                else:
                    f_authors.write(f"\t")
                
                try:
                    if 'bio' in data:
                        if isinstance(data['bio'], dict) and 'value' in data['bio']:
                            bio = data['bio']['value'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\h',' ').replace('\x08','').replace('\uf076',' ')
                            bio = bio.replace('\"','\\"')
                            f_authors.write(f"\t{bio}")
                        else:
                            bio = data['bio'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\h',' ').replace('\x08','').replace('\uf076',' ')
                            bio = bio.replace('\"','\\"')
                            f_authors.write(f"\t{bio}")
                    else:
                        f_authors.write(f"\t")
                except:
                    print("Error in bio\n")
                    print(data)
                    
                f_authors.write(f"\n")

                if 'photos' in data:
                    for p in data['photos']:
                        f_photos.write(f"{author}\t{p}\n")
                        
                if 'location' in data:
                    f_location.write(f"{author}\t{data['location']}\n")
            
            except Exception as e:
                print(e)
                print(line)
                print()            
            
    f_authors.close()
    f_photos.close()
    f_location.close()

    #f_location = open("authors_location.csv","w")

    with open("ol_dump_latest.txt", 'r') as file:
        round = 0
        
        for line in file:
            try:
                if "/type/author" not in line:
                    continue

                columns = line.split('\t')

                json_data = columns[-1].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\b',' ').replace('\x08','')
                data = json.loads(json_data)

                for k in data:
                    if isinstance(data[k], str):
                        data[k] = data[k].replace('\\t',' ').replace('\\r',' ').replace('\\n',' ')
                        
                if data['type'] != '/type/author':
                    continue
                
                if 'key' in data:
                    author = data['key'].split("/")[-1]
                    if author.startswith("OL") and 'location' in data:
                        #f_location.write(f"{author}\t{data['location']}\n")
                        print(data, data['location'],'\n')
                        if round>100:
                            break
                        round+=1
                    else:
                        continue
                else:
                    continue
            except Exception as e:
                print(e)
                print(line)
                print()

    f_location.close()

    # photos, subjects

    fields_var = []
    fields_arr = []

    with open("ol_dump_latest.txt", 'r') as file:
        round = 0
        for line in file:
            if "/type/author" in line:
                if round>1000000:
                    break
                round+=1
                columns = line.split('\t')
                json_data = columns[-1]
                data = json.loads(json_data)
                
                for fld in data:
                    if isinstance(data[fld], list):
                        if fld not in fields_arr:
                            fields_arr.append(fld)
                    else:
                        if fld not in fields_var:
                            fields_var.append(fld)

    f_authors.close()
    f_photos.close()

    print(fields_var)
    # ['bio', 'birth_date', 'body', 'cover_edition', 'create', 'created', 'date', 'death_date', 'description', 'entity_type', 'first_publish_date', 'first_sentence', 'fuller_name', 'key', 'last_modified', 'latest_revision', 'location', 'macro', 'name', 'numeration', 'personal_name', 'photograph', 'plugin', 'remote_ids', 'revision', 'role', 'subtitle', 'title', 'type', 'website', 'wikipedia']

    print(fields_arr)
    # ['alternate_names', 'authors', 'covers', 'dewey_number', 'excerpts', 'lc_classifications', 'links', 'photos', 'source_records', 'subject_people', 'subject_places', 'subject_times', 'subjects']


if __name__ == '__main__':
    main()

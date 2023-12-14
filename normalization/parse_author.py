import json
from utils import remove_special_char

"""
takes the ol_dump and based on different fields
that are deemed necessary, generates author csvs
from the json data column for input into db
"""

def main():
    # all no list fields for author object
    f_authors = open("testlib/authors.csv","w")

    # flatten the list of photos per author
    f_photos = open("testlib/authors_photos.csv","w")

    # flatten the list of location per author
    f_location = open("testlib/authors_location.csv","w")


    with open("ol_dump_latest.txt", 'r') as file:

        for line in file:
            try:
                # filter out non author entries
                # (some are works)
                if "/type/author" not in line:
                    continue

                columns = line.split('\t')

                json_data = columns[-1].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\b',' ').replace('\x08','')
                data = json.loads(json_data)

                for k in data:
                    if isinstance(data[k], str):
                        data[k] = remove_special_char(data[k])

                if 'type' not in data or 'key' not in data['type']:
                    continue
                
                # 2nd filter to remove non author entries 
                if data['type']['key'] != '/type/author':
                    continue

                # author ID
                if 'key' in data:
                    author = data['key'].split("/")[-1]
                    if author.startswith("OL"):
                        f_authors.write(f"{author}")
                    else:
                        continue
                else:
                    continue

                # ---------- NON-LIST FIELDS ----------

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
                    title = data['name']
                    f_authors.write(f"\t{title}")
                else:
                    f_authors.write(f"\t")

                if 'fuller_name' in data:
                    title = data['fuller_name']
                    f_authors.write(f"\t{title}")
                else:
                    f_authors.write(f"\t")

                if 'personal_name' in data:
                    title = data['personal_name']
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
                            bio = data['bio']['value']
                            f_authors.write(f"\t{bio}")
                        else:
                            bio = data['bio']
                            f_authors.write(f"\t{bio}")
                    else:
                        f_authors.write(f"\t")
                except:
                    print("Error in bio\n")
                    print(data)

                f_authors.write(f"\n")

                # ---------- LIST FIELDS ----------

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


if __name__ == '__main__':
    main()

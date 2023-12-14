import json
from random import random 
from utils import remove_special_char

"""
takes the ol_dump and based on different fields
that are deemed necessary, generates work csvs
from the json data column for input into db
"""

def main():
    # file for recording all non list fields for works entries
    f_works = open("works.csv","w")

    # file for recording all list fields for works entries
    f_covers = open("works_covers.csv","w")
    f_authors = open("works_authors.csv","w")
    f_original_languages = open("works_orginal_languages.csv","w")
    f_lc = open("works_lc_classifications.csv","w")
    f_subjects = open("works_subjects.csv","w")
    f_other_titles = open("works_other_titles.csv","w")
    f_translated_titles = open("works_translated_titles.csv","w")
    f_cover_editions = open("works_cover_editions.csv","w")
    f_dewey_number = open("works_dewey_number.csv","w")

    with open("../ol_dump_latest.txt", 'r') as file:

        for line in file:
            try:

                if "/type/work" not in line:
                    continue

                columns = line.split('\t')
                json_data = columns[-1]
                data = json.loads(json_data)

                if 'key' in data:
                    work = data['key'].split("/")[-1]
                    if work.startswith("OL"):
                        f_works.write(f"{work}")
                    else:
                        continue
                else:
                    continue

                # ---------- NON-LIST FIELDS ----------

                if 'created' in data:
                    f_works.write(f"\t{remove_special_char(data['created']['value'])}")
                else:
                    f_works.write(f"\t")

                if 'last_modified' in data:
                    f_works.write(f"\t{remove_special_char(data['last_modified']['value'])}")
                else:
                    f_works.write(f"\t")

                if 'revision' in data:
                    f_works.write(f"\t{remove_special_char(data['revision'])}")
                else:
                    f_works.write(f"\t")

                if 'latest_revision' in data:
                    f_works.write(f"\t{remove_special_char(data['latest_revision'])}")
                else:
                    f_works.write(f"\t")

                if 'title' in data:
                    title = remove_special_char(data['title'])
                    f_works.write(f"\t{title}")
                else:
                    f_works.write(f"\t")

                if 'subtitle' in data:
                    subtitle = remove_special_char(data['subtitle'])
                    f_works.write(f"\t{subtitle}")
                else:
                    f_works.write(f"\t")

                if 'first_publish_date' in data:
                    f_works.write(f"\t{remove_special_char(data['first_publish_date'])}")
                else:
                    f_works.write(f"\t")

                try:
                    if 'description' in data:
                        if isinstance(data['description'], dict) and 'value' in data['description']:
                            desc = remove_special_char(data['description']['value'])
                            desc = desc.replace('\"','\\"')
                            f_works.write(f"\t{desc}")
                        else:
                            desc = remove_special_char(data['description'])
                            desc = desc.replace('\"','\\"')
                            f_works.write(f"\t{desc}")
                    else:
                        f_works.write(f"\t")
                except:
                    print("Error in description\n")
                    print(data)

                if 'number_of_editions' in data:
                    f_works.write(f"\t{remove_special_char(data['number_of_editions'])}")
                else:
                    f_works.write(f"\t")

                f_works.write(f"\n")


                # ---------- LIST FIELDS ----------

                if 'covers' in data:
                    for c in data['covers']:
                        f_covers.write(f"{remove_special_char(work)}\t{remove_special_char(c)}\n")
                try:
                    if 'authors' in data:
                        for a in data['authors']:
                            if 'author' in a:
                                if isinstance(a['author'], dict):
                                    aid = a['author']['key'].split("/")[-1]
                                else:
                                    aid = a['author'].split("/")[-1]
                                f_authors.write(f"{work}\t{remove_special_char(aid)}\n")

                except:
                    print("Error in authors\n")
                    print(data)

                if 'original_languages' in data:
                    for ol in data['original_languages']:
                        if 'key' in ol:
                            f_original_languages.write(f"{work}\t{remove_special_char(ol['key'])}\n")

                if 'lc_classifications' in data:
                    for lc in data['lc_classifications']:
                        f_lc.write(f"{work}\t{remove_special_char(lc)}\n")

                if 'subjects' in data:
                    for s in data['subjects']:
                        f_subjects.write(f"{work}\t{remove_special_char(s)}\n")

                if 'other_titles' in data:
                    for ot in data['other_titles']:
                        f_other_titles.write(f"{work}\t{remove_special_char(ot)}\n")

                if 'translated_titles' in data:
                    for tt in data['translated_titles']:
                        if 'text' in tt:
                            f_translated_titles.write(f"{work}\t{remove_special_char(tt['text'])}\n")

                if 'cover_editions' in data:
                    for ce in data['cover_editions']:
                        f_cover_editions.write(f"{work}\t{remove_special_char(ce)}\n")

                if 'dewey_number' in data:
                    for dn in data['dewey_number']:
                        f_dewey_number.write(f"{work}\t{remove_special_char(dn)}\n")
            except Exception as e:
                print(e)
                print(line)
                print()

    f_works.close()
    f_covers.close()
    f_authors.close()
    f_original_languages.close()
    f_lc.close()
    f_subjects.close()
    f_other_titles.close()
    f_translated_titles.close()
    f_cover_editions.close()
    f_dewey_number.close()





if __name__ == '__main__':
    main()

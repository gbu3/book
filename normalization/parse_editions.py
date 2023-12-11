import json
from random import random 
import time

"""
takes the ol_dump and based on different fields
that are deemed necessary, generates edition csvs
from the json data column for input into db
"""

def main():
    f_editions = open("editions.csv","w")
    f_covers = open("editions_covers.csv","w")
    f_authors = open("editions_authors.csv","w")
    f_contributors = open('editions_contributors.csv',"w")
    f_genres = open('editions_genres.csv',"w")
    f_languages = open('editions_languages.csv',"w")
    f_lc_classifications = open('editions_lc_classifications.csv',"w")
    f_lccn = open('editions_lccn.csv',"w")
    f_publish_places = open('editions_publish_places.csv',"w")
    f_publishers = open('editions_publishers.csv',"w")
    f_series = open('editions_series.csv',"w")
    f_work_titles = open('editions_work_titles.csv',"w")
    f_works = open('editions_works.csv',"w")
    f_subjects = open("editions_subjects.csv","w")
    f_isbn10 = open("editions_isbn_10.csv","w")
    f_isbn13 = open("editions_isbn_13.csv","w")
    # f_ = open('editions_.csv',"w")
    # ['authors','covers','contributors','genres','languages','lc_classifications', 'lccn','publish_places', 'publishers','series','subjects','work_titles','works']

    start_time = time.time()

    def remove_special_char(s):
        if not isinstance(s,str):
            return s
        tmp_s = s.replace('\\t', ' ').replace('\\r',' ').replace('\\n',' ')
        return tmp_s.replace('\t', ' ').replace('\r',' ').replace('\n',' ').replace('\x08',' ').replace('\uf076',' ')

    with open("ol_dump_latest.txt", 'r') as file:
        round = 0
        for line in file:
            try:
                if "/type/edition" not in line:
                    continue

                columns = line.split('\t')
                json_data = columns[-1]
                data = json.loads(json_data)
                      
                if 'key' in data:
                    edition = data['key'].split("/")[-1]
                    if edition.startswith("OL"):
                        f_editions.write(f"{edition}")
                    else:
                        continue
                else:
                    continue

                if 'created' in data:
                    f_editions.write(f"\t{remove_special_char(data['created']['value'])}")
                else:
                    f_editions.write(f"\t")
                    
                if 'last_modified' in data:
                    f_editions.write(f"\t{remove_special_char(data['last_modified']['value'])}")
                else:
                    f_editions.write(f"\t")

                if 'revision' in data:
                    f_editions.write(f"\t{remove_special_char(data['revision'])}")
                else:
                    f_editions.write(f"\t")

                if 'latest_revision' in data:
                    f_editions.write(f"\t{remove_special_char(data['latest_revision'])}")
                else:
                    f_editions.write(f"\t")

                if 'title' in data:
                    title = remove_special_char(data['title'])
                    f_editions.write(f"\t{title}")
                else:
                    f_editions.write(f"\t")

                if 'subtitle' in data:
                    subtitle = remove_special_char(data['subtitle'])                                            
                    f_editions.write(f"\t{subtitle}")
                else:
                    f_editions.write(f"\t")

                if 'title_prefix' in data:
                    f_editions.write(f"\t{remove_special_char(data['title_prefix'])}")
                else:
                    f_editions.write(f"\t")
                
                if 'full_title' in data:
                    full_title = remove_special_char(data['full_title'])
                    f_editions.write(f"\t{full_title}")
                else:
                    f_editions.write(f"\t")
                
                if 'copyright_date' in data:
                    f_editions.write(f"\t{remove_special_char(data['copyright_date'])}")
                else:
                    f_editions.write(f"\t")
                
                if 'publish_date' in data:
                    f_editions.write(f"\t{remove_special_char(data['publish_date'])}")
                else:
                    f_editions.write(f"\t")
                
                if 'publish_country' in data:
                    f_editions.write(f"\t{remove_special_char(data['publish_country'])}")
                else:
                    f_editions.write(f"\t")
                    
                if 'by_statement' in data:
                    f_editions.write(f"\t{remove_special_char(data['by_statement'])}")
                else:
                    f_editions.write(f"\t")
                    
                if 'edition_name' in data:
                    f_editions.write(f"\t{remove_special_char(data['edition_name'])}")
                else:
                    f_editions.write(f"\t")

                if 'volume_number' in data:
                    f_editions.write(f"\t{remove_special_char(data['volume_number'])}")
                else:
                    f_editions.write(f"\t")
                
                try:
                    if 'description' in data:
                        if isinstance(data['description'], dict) and 'value' in data['description']:
                            desc = remove_special_char(data['description']['value'])
                            f_editions.write(f"\t{desc}")
                        else:
                            desc = remove_special_char(data['description'])
                            f_editions.write(f"\t{desc}")
                    else:
                        f_editions.write(f"\t")
                except:
                    f_editions.write(f"\t")
                    print("Error in description\n")
                    print(data)
                
                try:
                    if 'notes' in data:
                        if isinstance(data['notes'], dict) and 'value' in data['notes']:
                            notes = remove_special_char(data['notes']['value'])

                            f_editions.write(f"\t{notes}")
                        else:
                            notes = remove_special_char(data['notes'])
                            f_editions.write(f"\t{notes}")
                    else:
                        f_editions.write(f"\t")
                except:
                    f_editions.write(f"\t")
                    print("Error in notes\n")
                    print(data)
                
                
                if 'number_of_pages' in data:
                    f_editions.write(f"\t{remove_special_char(data['number_of_pages'])}")
                else:
                    f_editions.write(f"\t")
                
                if 'pagination' in data:
                    f_editions.write(f"\t{remove_special_char(data['pagination'])}")
                else:
                    f_editions.write(f"\t")
                    
                if 'translation_of' in data:
                    f_editions.write(f"\t{remove_special_char(data['translation_of'])}")
                else:
                    f_editions.write(f"\t")

                if 'dewey_decimal_class' in data:
                    f_editions.write(f"\t{remove_special_char(data['dewey_decimal_class'])}")
                else:
                    f_editions.write(f"\t")
                    
                f_editions.write(f"\n")
                
                if 'covers' in data:
                    for c in data['covers']:
                        f_covers.write(f"{edition}\t{remove_special_char(c)}\n")
                
                try:
                    if 'authors' in data:
                        for a in data['authors']:
                            if 'key' in a:
                                aid = a['key'].split("/")[-1]
                                f_authors.write(f"{edition}\t{remove_special_char(aid)}\n")
                except:
                    print("Error in authors\n")
                    print(data)
            
                if 'contributors' in data:
                    for c in data['contributors']:
                        if 'name' in c:
                            f_contributors.write(f"{edition}\t{remove_special_char(c['name'])}\n")
                
                if 'genres' in data:
                    for g in data['genres']:
                        f_genres.write(f"{edition}\t{remove_special_char(g)}\n")
                
                if 'languages' in data:
                    for l in data['languages']:
                        if 'key' in l:
                            f_languages.write(f"{edition}\t{remove_special_char(l['key'])}\n")
                if 'lc_classifications' in data:
                    for lc in data['lc_classifications']:
                        f_lc_classifications.write(f"{edition}\t{remove_special_char(lc)}\n")
                
                if 'lccn' in data:
                    for lc in data['lccn']:
                        f_lccn.write(f"{edition}\t{remove_special_char(lc)}\n")
                
                if 'publish_places' in data:
                    for pp in data['publish_places']:
                        f_publish_places.write(f"{edition}\t{remove_special_char(pp)}\n")
                
                if 'publishers' in data:
                    for pp in data['publishers']:
                        f_publishers.write(f"{edition}\t{remove_special_char(pp)}\n")
                    
                if 'series' in data:
                    for s in data['series']:
                        f_series.write(f"{edition}\t{remove_special_char(s)}\n")
                        
                if 'subjects' in data:
                    for s in data['subjects']:
                        f_subjects.write(f"{edition}\t{remove_special_char(s)}\n")
                        
                if 'isbn_10' in data:
                    for i10 in data['isbn_10']:
                        f_isbn10.write(f"{edition}\t{remove_special_char(i10)}\n")
                        
                if 'isbn_13' in data:
                    for i13 in data['isbn_13']:
                        f_isbn13.write(f"{edition}\t{remove_special_char(i13)}\n")

                        
                if 'work_titles' in data:
                    for wt in data['work_titles']:
                        f_work_titles.write(f"{edition}\t{remove_special_char(wt)}\n")
                
                if 'works' in data:
                    for w in data['works']:
                        if 'key' in w:
                            wk = w['key'].split('/')[-1]
                        f_works.write(f"{edition}\t{remove_special_char(wk)}\n")
                
            except Exception as e:
                print(e)
                print(line)
                print()

    print("--- %s seconds ---" % (time.time() - start_time)) # was 2746.689626932144 seconds

    f_editions.close()
    f_covers.close() 
    f_authors.close() 
    f_contributors.close() 
    f_genres.close() 
    f_languages.close() 
    f_lc_classifications.close() 
    f_lccn.close() 
    f_publish_places.close() 
    f_publishers.close() 
    f_series.close() 
    f_work_titles.close() 
    f_works.close() 
    f_subjects.close()
    f_isbn10.close()
    f_isbn13.close()

    fields_var = []
    fields_arr = []

    with open("ol_dump_latest.txt", 'r') as file:
        round = 0
        for line in file:
            if "/type/edition" in line:
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

    print(fields_var)
    # ['birth_date', 'body', 'bookweight', 'by_statement', 'classifications', 'copyright_date', 'coverimage', 'create', 'created', 'description', 'edition', 'edition_name', 'expected_type', 'first_sentence', 'full_title', 'ia_box_id', 'ia_id', 'ia_loaded_id', 'identifiers', 'key', 'last_modified', 'latest_revision', 'm', 'macro', 'name', 'notes', 'number_of_pages', 'ocaid', 'openlibrary', 'original_isbn', 'pagination', 'physical_dimensions', 'physical_format', 'plugin', 'property_name', 'publish_country', 'publish_date', 'revision', 'scan_on_demand', 'subtitle', 'title', 'title_prefix', 'translation_of', 'type', 'volume_number', 'weight', 'word_count']

    print(fields_arr)
    # ['authors','covers','contributors','genres','languages','lc_classifications', 'lccn','publish_places', 'publishers','series','subjects','work_titles','works']

if __name__ == '__main__':
    main()

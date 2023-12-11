import json
import re

"""
to fix all the issues with special characters messing up 
loading into the db from editions
"""

def main():
    f_works = open("t2","w")
    with open("t1", 'r') as file:
        for line in file:
            newline = re.sub(r'[^\x00-\x7F]+', lambda m: '\\u{:04X}'.format(ord(m.group(0))), line)
            newline = newline.replace("?","")
            #newline = line.replace('\x08','').replace('\uf076',' ').encode("ascii", "backslashreplace")
            f_works.write(f"{newline}\n")
    f_works.close()

    f_editions = open("e1.csv","w")

    with open("t4", 'r') as file:
        round = 0
        
        for line in file:
            try:
                if "/type/edition" not in line:
                    continue
                
                columns = line.split('\t')
                json_data = columns[-1].replace('\t', ' ').replace('\r',' ').replace('\n',' ')
                print(json_data)
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
                    f_editions.write(f"\t{data['created']['value']}")
                else:
                    f_editions.write(f"\t")
                    
                if 'last_modified' in data:
                    f_editions.write(f"\t{data['last_modified']['value']}")
                else:
                    f_editions.write(f"\t")

                if 'revision' in data:
                    f_editions.write(f"\t{data['revision']}")
                else:
                    f_editions.write(f"\t")

                if 'latest_revision' in data:
                    f_editions.write(f"\t{data['latest_revision']}")
                else:
                    f_editions.write(f"\t")

                if 'title' in data:
                    title = data['title'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\x08','').replace('\uf076',' ')
                    #title = title.encode("ascii", "backslashreplace")
                    f_editions.write(f"\t{title}")
                else:
                    f_editions.write(f"\t")

                if 'subtitle' in data:
                    subtitle = data['subtitle'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\x08','').replace('\uf076',' ')
                    #subtitle = subtitle.encode("ascii", "backslashreplace")
                    f_editions.write(f"\t{subtitle}")
                else:
                    f_editions.write(f"\t")

                if 'title_prefix' in data:
                    f_editions.write(f"\t{data['title_prefix']}")
                else:
                    f_editions.write(f"\t")
                
                if 'full_title' in data:
                    full_title = data['full_title'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\x08','').replace('\uf076',' ')
                    #full_title = full_title.encode("ascii", "backslashreplace")
                    f_editions.write(f"\t{full_title}")
                else:
                    f_editions.write(f"\t")
                
                if 'copyright_date' in data:
                    f_editions.write(f"\t{data['copyright_date']}")
                else:
                    f_editions.write(f"\t")
                
                if 'publish_date' in data:
                    f_editions.write(f"\t{data['publish_date']}")
                else:
                    f_editions.write(f"\t")
                
                if 'publish_country' in data:
                    f_editions.write(f"\t{data['publish_country']}")
                else:
                    f_editions.write(f"\tpublish_country")
                    
                if 'by_statement' in data:
                    f_editions.write(f"\t{data['by_statement']}")
                else:
                    f_editions.write(f"\tby_statement")
                    
                if 'edition_name' in data:
                    f_editions.write(f"\t{data['edition_name']}")
                else:
                    f_editions.write(f"\tedition_name")

                if 'volume_number' in data:
                    f_editions.write(f"\t{data['volume_number']}")
                else:
                    f_editions.write(f"\tvolume_number")
                
                try:
                    if 'description' in data:
                        if isinstance(data['description'], dict) and 'value' in data['description']:
                            desc = data['description']['value'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\h',' ').replace('\x08','').replace('\uf076',' ')
                            #desc = desc.replace('\"','\\"').encode("ascii", "backslashreplace")
                            f_editions.write(f"\t{desc}")
                        else:
                            desc = data['description'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\h',' ').replace('\x08','').replace('\uf076',' ')
                            #desc = desc.replace('\"','\\"').encode("ascii", "backslashreplace")
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
                            notes = data['notes']['value'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\h',' ').replace('\x08','').replace('\uf076',' ')
                            #notes = notes.replace('\"','\\"').encode("ascii", "backslashreplace")
                            f_editions.write(f"\t{notes}")
                        else:
                            notes = data['notes'].replace('\n',' ').replace('\r',' ').replace('\t',' ').replace('\h',' ').replace('\x08','').replace('\uf076',' ')
                            #notes = notes.replace('\"','\\"').encode("ascii", "backslashreplace")
                            f_editions.write(f"\t{notes}")
                    else:
                        f_editions.write(f"\t")
                except:
                    f_editions.write(f"\t")
                    print("Error in notes\n")
                    print(data)
                
                if 'number_of_pages' in data:
                    f_editions.write(f"\t{data['number_of_pages']}")
                else:
                    f_editions.write(f"\tnumber_of_pages")
                
                if 'pagination' in data:
                    f_editions.write(f"\t{data['pagination']}")
                else:
                    f_editions.write(f"\tpagination")
                    
                if 'translation_of' in data:
                    f_editions.write(f"\t{data['translation_of']}")
                else:
                    f_editions.write(f"\ttranslation_of")

                if 'dewey_decimal_class' in data:
                    f_editions.write(f"\t{data['dewey_decimal_class']}")
                else:
                    f_editions.write(f"\tdewey_decimal_class")
                    
                f_editions.write(f"\n")
        
            except Exception as e:
                print(e)
                print(line)
                print()

    f_editions.close()    

if __name__ == '__main__':
    main()


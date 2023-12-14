"""
helper functions when parsing the OL json
"""

def remove_special_char(s):
    if not isinstance(s,str):
        return s
    tmp_s = s.replace('\\t', ' ').replace('\\r',' ').replace('\\n',' ')
    return tmp_s.replace('\t', ' ').replace('\r',' ').replace('\n',' ').replace('\x08',' ').replace('\uf076',' ')

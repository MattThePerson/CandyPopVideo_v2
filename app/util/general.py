""" General purpose functions """
import os
import pickle

def pickle_save(obj, fn):
    with open(fn, "wb") as f:
        pickle.dump(obj, f)

def pickle_load(fn):
    if not os.path.exists(fn):
        return None
    with open(fn, "rb") as f:
        obj = pickle.load(f)
    return obj


# STRING NUMBER STUFF

def get_sortable_string_tuple(string) -> list:
    
    if not string:
        return []
    
    for c in ".:;-,'":
        string = string.replace(c, '')
    parts = [ p.strip() for p in string.lower().split(' ') if p != '' ]
    
    for i, part in enumerate(parts):
        num = extract_number_from_term(part)
        if num:
            parts[i] = '|{:0>9}'.format(num) # starts with | so the string sorts after pure letter strings
    
    return parts


def extract_number_from_term(x):

    if x.isnumeric():
        return int(x)
        
    number_words = 'one,two,three,four,five,six,seven,eight,nine,ten'.split(',')
    if x.lower() in number_words:
        return number_words.index(x.lower()) + 1
    
    num = _roman_to_int(x)
    if num:
        return num
    return None


def _roman_to_int(s):
    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50,
                'C': 100, 'D': 500, 'M': 1000}
    prev = 0
    total = 0

    for c in reversed(s.upper()):
        if c not in roman_map:
            return None
        val = roman_map[c]
        if val < prev:
            total -= val
        else:
            total += val
            prev = val

    return total


from unidecode import unidecode
import regex
import re 

def pollySplicer(text):
    textList = []
    stops = (".","!", "?"," ")
    count = 0
    curr = ""
    for char in text:
        if count > 2000 and char in stops:
            curr = curr + char
            textList.append(curr)
            curr = ""
            count = 0
            continue
        count+=1
        curr = curr + char
    textList.append(curr)
    return textList

def reduce_repeated_punctuation(text):
    # Replace consecutive periods with a single period
    text = re.sub(r'\.{2,}', '.', text)

    text = re.sub(r'(\d+)-(\d+)', r'\1 to \2', text)

    # Replace consecutive question marks with a single question mark
    text = re.sub(r'\?{2,}', '?', text)

    # Replace consecutive exclamation marks with a single exclamation mark
    text = re.sub(r'!{2,}', '!', text)
    
    text = re.sub(r'&{2,}', ' and ', text)
    text = re.sub(r'&', ' and ', text)

    return text

def getGender(text):
    # male = len( regex.findall( r"(?<=(me|I|myself)\s*)\((\d{2}[mM])\)", text, regex.IGNORECASE))
    male = len( regex.findall( r"((?<=(me|I|myself|my)\s*)\(?\s*(\d{2}[mM])\)?)", text, regex.IGNORECASE))
    female = len(regex.findall(r"((?<=(me|I|myself|my)\s*)\(?\s*(\d{2}[fF])\)?)", text, regex.IGNORECASE))
    if male > 0: return 999999
    if female > 0: return -999999
    checker = regex.findall(r"\bmy\s+.*?(wife|girlfriend)\b", text, regex.IGNORECASE)
    for i in checker: 
        if i[-10:].lower() == 'girlfriend':
            if len(i) < 20:
                male+=1
        elif i[-4:].lower() == 'wife':
            if len(i) <16:
                male+=1
    checker = regex.findall(r"\bmy\s+.*?(boyfriend|husband)\b", text, regex.IGNORECASE)
    for i in checker: 
        if i[-9:].lower() == 'boyfriend':
            if len(i) < 19:
                female+=1
        elif i[-7:].lower() == 'husband':
            if len(i) <18:
                female+=1    
    return male-female

# Deprecated
def changeAcro(txt):
    acronyms = {}
    if txt.lower() in acronyms or re.sub(r'[^a-zA-Z]', "",txt.lower()) in acronyms:
        if txt.lower() in acronyms: return acronyms[txt.lower()]
        else: return  re.sub(re.sub(r'[^a-zA-Z]', "",txt.lower()), acronyms[re.sub(r'[^a-zA-Z]', "",txt.lower())] ,txt.lower())
    else: return txt

# Deprecated
# def getTextFromFile(file):
#     txtFile = open(file, encoding='utf-8', errors='ignore', mode='r')
#     raw = ""
#     for i in txtFile:
#         for k in i.split(" "):
#             for z in k: 
#                 z = changeAcro(z)
#             if k == "-" or k== "(" or k==")" :
#                 raw += changeAcro(k)
#             else: raw += " " + changeAcro(k)
#     return unidecode(reduce_repeated_punctuation(raw.replace('“', '"').replace('”', '"').replace("’", "'")))       

#Text processing
# preprocess, generate ngrams, load docs, extract files



import os
import re
import json
import string

def preprocess_text(text): #to clean text and create a list of lowercase words by 1.lowercase 2.replacing punctuation with space 3.merging multiple whitespaces into single 
    if not text:
        return [] #if input is false, return empty list
    text=text.lower()
    text=re.sub(f"[{re.escape(string.punctuation)}]"," ",text) #punctuation handling
    text = re.sub(r"\s+", " ", text).strip() #multiple space handling
    return text.split()

def generate_ngrams(words,n=3): #to generate all ngrams from a list of words
    result=[] #list to store ngram
    if len(words)<n:
        return [] #ngram generation needs min 4 words
    for i in range(len(words)-n+1): #no. of possible ngrams
        gram=tuple(words[i:i+n])
        result.append(gram)
    return result #a list of ngram tuples

def load_documents_from_folder(folder_path): #returns readable documents from folder, deals with txt and json files
    #parameter: folder_path is path to reference document's database directory
    dataset=[]
    if not os.path.exists(folder_path):
        return dataset #docs with no extractable content are skipped
    for filename in os.listdir(folder_path): #goes through each file in folder
        filepath=os.path.join(folder_path,filename) #creates full path for file
        content="" #empty content
        try: #error handling
            if filename.endswith(".txt"):
                with open(filepath,"r",encoding="utf-8",errors="ignore") as f:
                    content=f.read() #read all text from file if file is .txt
            elif filename.endswith(".json"):
                with open(filepath,"r",encoding="utf-8",errors="ignore") as f:
                    data=json.load(f) #load json if file is .json
                    if isinstance(data,dict): #if dict, get "text " key value
                        content=data.get("text","")
                    elif isinstance(data,list):
                        content=" ".join([item.get("text","") for item in data]) #if list of items, join all text values in a string
        except Exception:
            pass
        if content:
            dataset.append({
                "doc_id": filename,
                "text": content
            }) #a list of dict 
    return dataset 

def extract_single_file_content(filepath): #reads and returns text content of a single file
    if not filepath or not os.path.exists(filepath):
        return "" #empty string returned when unsupported type
    try:
        if filepath.endswith(".txt"): #if its a .txt file
            with open(filepath,"r",encoding="utf-8",errors="ignore") as f: #opened in read mode
                return f.read() #text returned from the file
        elif filepath.endswith(".json"): #if its a .json file
            with open(filepath,"r",encoding="utf-8",errors="ignore") as f: #open file
                data=json.load(f) #load json
                if isinstance(data,dict): #check if json is a dict
                    return data.get("text","") #returns value of "text" key else empty if not found
                else:
                    return ""
    except Exception:
        return "" #if error return empty string
#Trie Data Structure Implementation

#Role: Core ADT, Trie construction, insertion, and search
#Functions: create_node, insert_phrase, search_phrase, search_prefix, collect_phrases



def create_node():#most common implementation for a trie is to use dictionary 
#creates node
#children for branching, is_end to indicicate the end of ngram 
    return {
            "children": {}, #dictionary that represent nodes inside trie
            "is_end": False, #end of phrse
            "doc_ids": [], #a list that stores end of phrase
            "frequency": 0  #tracks visits to specific node
        }


def insert_phrase(trie, phrase, doc_id): #each word of ngram becomes a node
#inserts a a sewq of n-grams into the trie structure
#phir list ko check krta hai to keep doc ids

    current_node = trie
    #iterate thorugh each word in the phrase to build its path

    for word in phrase:
        if word not in current_node["children"]: #if word doesnt exist create new node
            current_node["children"][word] = create_node()
        
        #then move inside to its child node
        current_node = current_node["children"][word]
        current_node["frequency"] += 1 #incriment
            
    current_node["is_end"] = True #mark it as the end

    if doc_id not in current_node["doc_ids"]:  #check if this document ID is already recorded for this specific phrase
        current_node["doc_ids"].append(doc_id)


def search_phrase(trie, ngram):
    ##exact match dhoondta hai aur documents ki list return krta
    #follows the sequence word by word through the nested dictionaries of the trie
    #check O(n)  items
    current_node = trie
    for word in ngram:
        
        if word not in current_node["children"]: #if word is missing or not found
            return None #this phrase doesnt exist
        
        current_node = current_node["children"][word] #move the pointer deepeer like insert phrase

    #after finding the fullpath verify if its marked as 'end' phrase
    #return docs only if its a valid end node
    if current_node["is_end"]:
        return current_node["doc_ids"]
    return None


def search_prefix(trie, prefix):
    #checks if a sequence of words exists as a prefix in the trie
    #does not CARE ABOUT IS_END
    #why needed? 
    current_node = trie

    #looping throygh the words in the prefix
    for word in prefix:
        
        if word not in current_node["children"]:
            return None
        
        current_node = current_node["children"]
#returns the actual node we reached 
#this allows the sys to look at metadata like freq at that spot
    return current_node


def collect_phrases(node, current_phrase = None, results=None):
    #this is a DFS which recursivley goes deeper as much as possible down a branch for one phrase.
    #turns the trie back into a flat list of data so it is readable

    #becuz it collects all complete phrases that are stored in a trie
    #node is a dic, contains the links to the next possible words

    #current_pjrase is list of words stores the seq of words found in current node, remembers fullphrase.

    #results is a list that adds the ohrases fonund 
 

    if current_phrase is None: #agar pahli dafa call kya hai toh aur koi list nhi hai toh
        current_phrase = []    #create an empty list

    if results is None:##agar pahli dafa call kya hai toh aur results ki list nhi hai toh
        results = []  #make a results list to STOREE THE OHRASES

    if node["is_end"]: #checker, is the current word end of a full phrase?

        results.append((tuple(current_phrase),  #yes, grab the phrase and put these in list
                        list(node["doc_ids"]), node["frequency"]))

    for word, child in node["children"].items():    #the MAIN BRANHCING LOGIC.. looking at every child word branching out
        collect_phrases(child, current_phrase + [word], results) #recirsive call move into that child word and track its phrase path
    
    return results
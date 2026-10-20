import re
from trie_adt import search_phrase #matches returned after looking up phrase

def match_phrases(trie, query_ngrams): #query_ngrams is a list of ngrams
    matches = [] #empty list to store results 
    for ngram in query_ngrams: #each ngram in the inputted list
        found = search_phrase(trie,ngram) #we check if ngram exists
        if found:
            matches.append({"phrase":" ".join(ngram), #when found, new entry to matches list, mgram made into single stirng
                            "sources":list(found)}) ##dodcuments with the phrases put into list
    return matches #final list returned 

def longest_phrase_match(trie, words): #longest matching phrase
    longest = [] #empty list to store longest matched phrases
    i=0 #scans word list
    while i < len(words): #loops through words list till end
        node = trie #traversal started from root of trie for each position of index i 
        end = -1 #ending index of the longest valid match
        for j in range(i,len(words)):  #search expanded from position i to find longest match
            if words[j] in node["children"]: #checks if word exists as a child node in trie
                node = node["children"][words[j]]  #child in trie
                if node["is_end"]: #end changed to j
                    end = j
            else:
                break #word not found so no check further
        if end != -1 and (end-i+1) >= 3: #valid phrase found and phrase length has to be more than 3 words
            longest.append(" ".join(words[i:end+1])) #i to end in a string, added to longest list
            i = end+1 #i moved past matvhed phrase
        else:
            i += 1 #no valid phrase so new word
    return longest #list of longest phrase

def compute_similarity(matched, total): #similarity percentage calculated here
    if total == 0:
        return 0
    percentage = (matched/total)*100
    return round(percentage,2)


def aggregate_source_scores(matches, total):
    counts = {} 
    for m in matches: #each match in matches list
        for doc in m["sources"]: #all documents where phrase found 
            if doc in counts: #if doc in counts, count increased 
                counts[doc] += 1
            else:
                counts[doc] = 1 #if not so added
    result = [] #list to store final output 
    for doc in counts: #each document in counts dictionary
        c = counts[doc] #number of matches for that document
        similarity = compute_similarity(c,total) 
        result.append((doc,c,similarity)) #result as tuple stored
    def sort_by_count(item):  #helper function for sorting
        return item[1] #sort using the match count
    result.sort(key=sort_by_count,reverse = True) #list sorted
    return result #final sorted list

def generate_final_report(
    score, matches, longest_seq, doc_name,
    db_count, total_query_ngrams=0, query_words=None,
    output_widget=None
):
#prints the plagirsm report and shows the highlited text in gui
#report includes:
#   header with doc info and overall similarity score
#   verdict (final output)
#   breakdown of match per source
#   most plagiarised source
#   plafiared text highlighted in red

#parameters:
#   score:      similarity percentage
#   matches:    list from match_phrase
#   doc name:   sus[ect doc
#   db count:   no of refrence docs
#   total_query_ngrams: total ngrams in suspect doc
#   query_words: list pf preprocessed words
#   output widget: tkiter text widget needed for higjlighting  


    print("\n" + "═" * 60)
    print("           INTELLICHECK PLAGIARISM ANALYSIS REPORT")
    print("═" * 60)
    print(" Query Document:", doc_name)
    print(" Reference DB :", db_count, "documents indexed")
    print(" Similarity :", score, "%")
    print("-" * 60)

   # verdict thresholds - >70% is flagged, 30-70 is a warning, below is fine
    if score > 70:
        print(" VERDICT: HIGH PLAGIARISM DETECTED")
    elif score > 30:
        print("  VERDICT: MODERATE SIMILARITY DETECTED")
    else:
        print(" VERDICT: DOCUMENT APPEARS ORIGINAL")

   
    if longest_seq:
        print("\n TOP LONGEST COPIED SEQUENCES:")
        # Sort by length descending and show top 3
        for seq in sorted(longest_seq, key=len, reverse=True)[:3]:
            print(f"   • \"{seq}\"")
            
    print("-" * 60)

    #  Per-source breakdown
    if matches and total_query_ngrams:
        ranked = aggregate_source_scores(matches, total_query_ngrams)

        print("\n SOURCE DOCUMENT BREAKDOWN (via Trie doc_ids):")
        header = f"   {'Rank':<6}{'Document':<36}{'Phrases Matched':<18}Contribution"
        print(header)
        print("   " + "-" * 72)

        for i, (doc, count, pct) in enumerate(ranked, 1):
            bar = "" * max(1, int(pct / 5))
            tag = "  ◄ HIGHEST MATCH" if i == 1 else ""
            print(
                f"   {i:<6}{doc:<36}{count:<18} {pct}%  {bar}{tag}"
            )

        top_doc, top_count, top_pct = ranked[0]
        print("\n MOST PLAGIARISED FROM :", top_doc)
        print("   Phrases copied        :", top_count)
        print("   Contribution to score :", score, "%")

    #COLOR highlights
    if matches and query_words and output_widget is not None:
        print("\n" + "─" * 60)
        print(" RECONSTRUCTED TEXT WITH PLAGIARISM HIGHLIGHTED:\n")

        # Build a set of all plagiarised phrases, longest first so
        # longer spans are marked before shorter overlapping ones.
        plagiarised_phrases = sorted(
            set(m["phrase"] for m in matches),
            key=lambda x: -len(x)
        )

        # Tokenise the full text into (word, is_plagiarised) pairs.
        full_text = " ".join(query_words)

        # Build a character-level boolean mask: True = plagiarised.
        mask = [False] * len(full_text)
        for phrase in plagiarised_phrases:
            for m in re.finditer(r"\b" + re.escape(phrase) + r"\b", full_text):
                for idx in range(m.start(), m.end()):
                    mask[idx] = True

        # Configure tkinter text tags (set once; safe to call repeatedly).
        output_widget.tag_configure(
            "plagiarised",
            background ="#e74c3c",   # vivid red background
            foreground="#ffffff",   # white text
        )
        output_widget.tag_configure(
            "normal_text",
            background="",         # inherit console background
            foreground="#d4d4d4",   # normal console text colour
        )

        # Walk through the masked text and insert coloured segments.
        i = 0
        while i < len(full_text):
            # Find the end of the current run (same mask value).
            j = i + 1
            while j < len(full_text) and mask[j] == mask[i]:
                j += 1

            segment = full_text[i:j]
            tag = "plagiarised" if mask[i] else "normal_text"
            output_widget.insert("end", segment, tag)
            i = j

        output_widget.insert("end", "\n")
        output_widget.see("end")

    elif matches and query_words and output_widget is None:
        # Fallback: plain print if no widget supplied
        phrases = set(m["phrase"] for m in matches)
        text = " ".join(query_words)
        for p in sorted(phrases, key=lambda x: -len(x)):
            text = re.sub(r"\b" + re.escape(p) + r"\b", f"[{p}]", text)
        print(text)

    print("\n" + "═" * 60)
#Main Entry Point & GUI
#Integrates all three member modules:
#trie_adt                (Trie ADT)
#text_processing         (Text Processing)
#report_generation       (Matching & Reporting)

import os
import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# Member module imports
from trie_adt import (
    create_node,
    insert_phrase,
    search_phrase,
    search_prefix,
    collect_phrases,
)
from text_processing import (
    preprocess_text,
    generate_ngrams,
    load_documents_from_folder,
    extract_single_file_content,
)
from report_generation import (
    match_phrases,
    longest_phrase_match,
    compute_similarity,
    generate_final_report,
)



def run_main_system(output_widget):

#1. prompts user to select the reference document folder first
#2. prompts user to select the suspect document to check
#3. builds the Trie index from all reference documents
#4. processes the suspect document and runs phrase matching
#5. denerates and prints the final report
#######
#1)select feference folder
    ref_folder = filedialog.askdirectory(title="Select Reference Document Folder")
    if not ref_folder:
        return

#2)select suspect doc
    sus_file = filedialog.askopenfilename(
        title="Select Suspect Document",
        filetypes=[("Text/JSON Files", "*.txt *.json"), ("All Files", "*.*")]
    )
    if not sus_file:
        return

    output_widget.delete("1.0", tk.END)
    print("Initializing IntelliCheck Engine...")
    print("Loading reference documents from:", os.path.basename(ref_folder))

#3)build Trie index
    trie_root = create_node()
    reference_docs = load_documents_from_folder(ref_folder)
    
    if not reference_docs:
        print("Error: No valid .txt or .json files found in the reference folder.")
        return
    for doc in reference_docs:
        words = preprocess_text(doc["text"])
        # generate_ngrams is a generator; convert to list for insertion loop
        phrases = list(generate_ngrams(words, n=3))
        for p in phrases:
            insert_phrase(trie_root, p, doc["doc_id"])
    print("Successfully indexed", len(reference_docs), "documents into the Trie.")

    #collect_phrases 
    #we use this to audit the database and show unique phrase counts
    db_inventory = collect_phrases(trie_root)
    print("Database Stats:", len(db_inventory), "unique n-grams stored in Trie.")
    #NEW: Show the top 5 most frequent phrases in the database
    print("\n--- Top Database Entries (Common Phrases) ---")
    
    #sort by frequency (index 2 of the tuple) in reverse
    sorted_inventory = sorted(db_inventory, key=lambda x: x[2], reverse=True)
    
    for phrase_tuple, docs, freq in sorted_inventory[:5]:
        #join words back into a readable string
        phrase_str = " ".join(phrase_tuple) 
        
        #using .format() for the detailed breakdown
        output_line = " • '{}' found {} times in {} document(s)".format(
            phrase_str, freq, len(docs)
        )
        print(output_line)
    print("---------------------------------------------\n")
#4)process Suspect Document
    print("Analyzing:", os.path.basename(sus_file), "...")
    sus_raw_text = extract_single_file_content(sus_file)
    sus_words = preprocess_text(sus_raw_text)

    if len(sus_words) >= 2:  #perform a prefix-check on the document's opening words
        intro_prefix = sus_words[:2]
        prefix_node = search_prefix(trie_root, intro_prefix)
        if prefix_node:
            print("System Insight: The sequence", ' '.join(intro_prefix), "already exists in the corpus.")

    #generate_ngrams is now a generator for efficiency
    sus_ngrams_list = list(generate_ngrams(sus_words, n=3))

    if not sus_ngrams_list:
        print("Note: Suspect document is too short for 3-word phrase analysis.")
        return

#5)run Analysis
    matches = match_phrases(trie_root, sus_ngrams_list)
    longest = longest_phrase_match(trie_root, sus_words)
    score = compute_similarity(len(matches), len(sus_ngrams_list))

#6)generate report
    generate_final_report(
        score=score,
        matches=matches,
        longest_seq=longest,
        doc_name=os.path.basename(sus_file),
        db_count=len(reference_docs),
        total_query_ngrams=len(sus_ngrams_list),
        query_words=sus_words,
        output_widget=output_widget
    )


# GUI SETUP

def setup_gui():
    window = tk.Tk()
    window.title("IntelliCheck – Plagiarism Detector")
    window.geometry("900x700")
    window.configure(bg="#0d0d1a")  # Cyberpunk Dark Theme

    # ── Header ───────────────────────────────────────────────
    header_frame = tk.Frame(window, bg="#1a1a2e", height=80)
    header_frame.pack(fill="x")
    
    lbl_title = tk.Label(
        header_frame,
        text="INTELLICHECK",
        font=("Helvetica", 24, "bold"),
        bg="#1a1a2e",
        fg="#00d4ff"
    )
    lbl_title.pack(pady=20)

    # ── Control Panel ────────────────────────────────────────
    ctrl_frame = tk.Frame(window, bg="#0d0d1a")
    ctrl_frame.pack(pady=20)

    btn_start = tk.Button(
        ctrl_frame,
        text="START PLAGIARISM CHECK",
        font=("Helvetica", 16, "bold"),
        bg="#00d4ff",
        fg="#0d0d1a",
        activebackground="#008cb3",
        relief="flat",
        padx=20,
        pady=10,
        cursor="hand2",
        command=lambda: run_main_system(output)
    )
    btn_start.pack(side="left", padx=10)

    btn_exit = tk.Button(
        ctrl_frame,
        text="EXIT",
        font=("Helvetica", 12),
        bg="#33334d",
        fg="white",
        relief="flat",
        padx=14,
        pady=8,
        cursor="hand2",
        command=window.destroy,
    )
    btn_exit.pack(side="right")

    # ── Output console ───────────────────────────────────────
    output = scrolledtext.ScrolledText(
        window,
        font=("Consolas", 12),
        bg="#0d0d1a",
        fg="#d4d4d4",
        insertbackground="white",
        selectbackground="#264f78",
        relief="flat",
        padx=14,
        pady=10,
    )
    output.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ── Redirect stdout → output widget ─────────────────────
    class WidgetWriter:
        def __init__(self, widget):
            self.widget = widget

        def write(self, s):
            self.widget.insert(tk.END, s)
            self.widget.see(tk.END)
            self.widget.update_idletasks()

        def flush(self):
            pass

    sys.stdout = WidgetWriter(output)

    # ── Welcome message ──────────────────────────────────────
    print("Welcome to IntelliCheck!\n")
    print("Click  🚀 START PLAGIARISM CHECK  to begin.")
    print("You will be asked to:")
    print("  1️⃣   Select the reference document folder  (source corpus)")
    print("  2️⃣   Select the suspect document to check\n")
    print("─" * 60)

    window.mainloop()


if __name__ == "__main__":
    setup_gui()
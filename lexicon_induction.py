import subprocess
import argparse
import string
import chardet
import numpy as np
from scipy.spatial import distance

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        rawdata = file.read()
        result = chardet.detect(rawdata)
        return result['encoding']
        print("Detected encoding:", result['encoding'])

def preprocess_text(corpus_path, output_file):
    encodage = detect_encoding(corpus_path)
    with open(corpus_path, 'r', encoding=encodage) as file:
        text = file.read().lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
    with open(output_file, 'w', encoding='utf-8') as clean_file:
        clean_file.write(text)

def generate_word_embeddings(corpus_path, output_path):
    command = ['./fastText/fasttext', 'skipgram', '-input', corpus_path, '-output', output_path, '-minCount', '1', '-wordNgrams', '1', '-minn', '0', '-maxn', '0', '-dim', '300']
    subprocess.run(command)

def generate_crossLingual_map_embeddings(src_emb, trg_emb, src_mapped_emb, trg_mapped_emb):
    command = [
        'python3', './vecmap/map_embeddings.py', '--acl2018',
        src_emb, trg_emb, src_mapped_emb, trg_mapped_emb
    ]
    subprocess.run(command)


def load_embeddings(file_path):
    embeddings = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split()
            word = parts[0]
            vec = np.array(parts[1:], dtype=float)
            embeddings[word] = vec
    return embeddings

def generate_dictionary(src_embeddings, trg_embeddings):
    #convertir les embedding en matrice de vecteurs de mots
    src_words, src_vecs = zip(*src_embeddings.items())
    trg_words, trg_vecs = zip(*trg_embeddings.items())
    src_matrix = np.array(src_vecs)
    trg_matrix = np.array(trg_vecs)
    
    # calculer la similarité cosinus
    cosine_similarities = 1 - distance.cdist(src_matrix, trg_matrix, 'cosine')
    
    # trouver l'index de la plus grande similarité
    best_matches = np.argmax(cosine_similarities, axis=1)
    
    # Créer le dictionnaire
    dictionary = {src_word: trg_words[best_index] for src_word, best_index in zip(src_words, best_matches)}
    return dictionary

def write_dictionary_to_file(dictionary, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for src, trg in dictionary.items():
            file.write(f"{src}\t{trg}\n")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Lexicon Induction IT-EN")
    parser.add_argument("--source_corpus", required=True, help="Chemin vers le corpus de texte source")
    parser.add_argument("--target_corpus", required=True, help="Chemin vers le corpus de texte cible")
    return parser.parse_args()


if __name__ == "__main__":

    # Analyser les arguments en ligne de commande
    args = parse_arguments()
    # pretraitement des corpus de texte (normalisation, déponctuation)
    clean_corpus_source_path = "clean_corpus_source.txt"
    clean_corpus_target_path = "clean_corpus_target.txt"

    print("--------------------- Preprocessing du corpus de texte source -------------------------\n")
    # preprocessing source corpus
    preprocess_text(args.source_corpus, clean_corpus_source_path)

    print("--------------------- Preprocessing du corpus de texte Cible -------------------------\n")

    # preprocessing target corpus
    preprocess_text(args.target_corpus, clean_corpus_target_path)

    # Génération des embeddings pour le corpus source
    print("--------------------- Génération des embeddings monolingue pour le corpus source -------------------------\n")
    source_output_path = "source_embeddings"
    generate_word_embeddings(clean_corpus_source_path, source_output_path)
    print("--------------------- Génération des embeddings monolingue pour le corpus target -------------------------\n")
    target_output_path = "target_embeddings"
    generate_word_embeddings(clean_corpus_target_path, target_output_path)

    # generation des embeddings multilingue avec vec2map
    source_cross_path = "source_crosslingual.vec"
    target_cross_path = "target_crosslingual.vec"

    ext = ".vec"
    print("--------------------- Génération des embeddings multilingue pour les corpus source & cible -------------------------\n")
    generate_crossLingual_map_embeddings(source_output_path+ext , target_output_path+ext, source_cross_path, target_cross_path)

    print("--------------------- Induction de lexique  -------------------------\n")
    source = load_embeddings(source_cross_path)
    target = load_embeddings(target_cross_path)
    Dictionnary = generate_dictionary(source, target)
    write_dictionary_to_file(Dictionnary, "Dico_IT-EN.txt")

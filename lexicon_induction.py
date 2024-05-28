import subprocess
import argparse
import string
import chardet
import numpy as np
from scipy.spatial import distance
import gensim.downloader as api
from gensim.models import KeyedVectors
from huggingface_hub import hf_hub_download
model_pretrained_it = KeyedVectors.load_word2vec_format(hf_hub_download(repo_id="Word2vec/wikipedia2vec_itwiki_20180420_300d", filename="itwiki_20180420_300d.txt"))

model_pretrained_en = KeyedVectors.load_word2vec_format(hf_hub_download(repo_id="Word2vec/wikipedia2vec_enwiki_20180420_300d", filename="enwiki_20180420_300d.txt"))
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
        
def get_W2V_words_from_corpus(file_path):
    try:
        # Créer un ensemble pour stocker les mots uniques
        unique_words = set()
        
        # Ouvrir le fichier en mode lecture
        with open(file_path, 'r', encoding='utf-8') as file:
            # Lire le fichier ligne par ligne
            for line in file:
                # Normaliser la ligne pour éviter les variations dues à la casse
                line = line.lower()
                # Remplacer les signes de ponctuation communs par des espaces
                for char in ",.!?;:()[]{}\"'":
                    line = line.replace(char, " ")
                # Diviser la ligne en mots sur les espaces
                words = line.split()
                # Ajouter les mots à l'ensemble des mots uniques
                unique_words.update(words)
        
        # La taille de l'ensemble est le nombre de mots uniques dans le fichier
        return unique_words
    except FileNotFoundError:
        print("Erreur : Le fichier spécifié n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier: {e}")
        
def count_non_empty_lines(file_path):
    try:
        # Initialiser un compteur pour les lignes non vides
        non_empty_line_count = 0
        
        # Ouvrir le fichier en mode lecture
        with open(file_path, 'r', encoding='utf-8') as file:
            # Lire le fichier ligne par ligne
            for line in file:
                # Vérifier si la ligne n'est pas vide (ignorer les espaces blancs)
                if line.strip():
                    non_empty_line_count += 1
        
        # Afficher le nombre de lignes non vides
        return non_empty_line_count
    
    except FileNotFoundError:
        print("Erreur : Le fichier spécifié n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier: {e}")
        
def generate_pretrained_w2v_it_en(words_en, words_it):
    with open("target_embeddings1.vec", "w", encoding="utf-8") as f_out:   
        f_out.write(f"{len(words_en)} 300\n")
        for word_en in words_en:
            try:
                embedding = model_pretrained_en[word_en]
                f_out.write(f"{word_en} {' '.join(map(str, embedding))}\n")
            except KeyError:
                # Si le mot n'existe pas dans le modèle, passez simplement à l'itération suivante
                continue
    count_words_en = count_non_empty_lines("./target_embeddings1.vec")
    with open("target_embeddings1.vec", "r", encoding="utf-8") as f_in:
        with open("target_embeddings.vec", "w", encoding="utf-8") as f_in_out:
            f_in_out.write(f"{count_words_en - 1} 300\n")
            for line in f_in:
                f_in_out.write(f"{line}\n")
        
    with open("source_embeddings1.vec", "w", encoding="utf-8") as f_out:
        f_out.write(f"{len(words_it)} 300\n")
        for word_it in words_it:
            try:
                embedding = model_pretrained_it[word_it]
                f_out.write(f"{word_it} {' '.join(map(str, embedding))}\n")
            except KeyError:
                continue
    count_words_it = count_non_empty_lines("./source_embeddings1.vec")
    with open("source_embeddings1.vec", "r", encoding="utf-8") as f_in:
        with open("source_embeddings.vec", "w", encoding="utf-8") as f_in_out:
            f_in_out.write(f"{count_words_it - 1} 300\n")
            for line in f_in:
                f_in_out.write(f"{line}\n")
                
def generate_word_embeddings(corpus_path, output_path):
    command = ['./fastText/fasttext', 'skipgram', '-input', corpus_path, '-output', output_path, '-minCount', '1', '-wordNgrams', '1', '-minn', '0', '-maxn', '0', '-dim', '200']
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
        next(file)
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
    
    cosine_similarities = 1 - distance.cdist(src_matrix, trg_matrix, 'cosine')
    
    best_matches = np.argmax(cosine_similarities, axis=1)
    
    dictionary = {src_word: trg_words[best_index] for src_word, best_index in zip(src_words, best_matches)}
    return dictionary

def write_dictionary_to_file(dictionary, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for src, trg in dictionary.items():
            file.write(src + "\t" + trg + "\n")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Lexicon Induction IT-EN")
    parser.add_argument("--source_corpus", required=True, help="Chemin vers le corpus de texte source")
    parser.add_argument("--target_corpus", required=True, help="Chemin vers le corpus de texte cible")
    return parser.parse_args()


if __name__ == "__main__":

    # Analyser les arguments en ligne de commande
    args = parse_arguments()

    clean_corpus_source_path = "clean_corpus_source.txt"
    clean_corpus_target_path = "clean_corpus_target.txt"

    print("--------------------- Preprocessing du corpus de texte source -------------------------\n")
    # preprocessing source corpus
    preprocess_text(args.source_corpus, clean_corpus_source_path)

    print("--------------------- Preprocessing du corpus de texte Cible -------------------------\n")

    # preprocessing target corpus
    preprocess_text(args.target_corpus, clean_corpus_target_path)

    print("--------------------- Génération des embeddings monolingue pour le corpus source -------------------------\n")
    source_output_path = "source_embeddings"
    # generate_word_embeddings(clean_corpus_source_path, source_output_path)
    words_it = get_W2V_words_from_corpus(clean_corpus_source_path)
    words_en = get_W2V_words_from_corpus(clean_corpus_target_path)
    generate_pretrained_w2v_it_en(words_it, words_en)
    # print("--------------------- Génération des embeddings monolingue pour le corpus target -------------------------\n")
    target_output_path = "target_embeddings"
    # generate_word_embeddings(clean_corpus_target_path, target_output_path)

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

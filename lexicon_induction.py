import subprocess
import argparse
import string

def preprocess_text(corpus_path, output_file):
    with open(corpus_path, 'r', encoding='utf-8') as file:
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

def generate_lexicon_induction(source_cross_path, target_cross_path):
    command = [
        'python3', './vecmap/eval_translation.py',
        source_cross_path, target_cross_path, '-d', 'IT-EN.DICT'
    ]
    subprocess.run(command)

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
    print("--------------------- Génération des embeddings monolingue pour le target source -------------------------\n")
    target_output_path = "target_embeddings"
    generate_word_embeddings(clean_corpus_target_path, source_output_path)

    # generation des embeddings multilingue avec vec2map
    source_cross_path = "source_crosslingual.vec"
    target_cross_path = "target_crosslingual.vec"

    ext = ".vec"
    print("--------------------- Génération des embeddings multilingue pour les corpus source & cible -------------------------\n")
    generate_crossLingual_map_embeddings(source_output_path+ext , target_output_path+ext, source_cross_path, target_cross_path)

    print("--------------------- Induction de lexique  -------------------------\n")
    generate_lexicon_induction(source_cross_path, target_cross_path)
import sys

def calculate_vocabulary_size(file_path):
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
        vocabulary_size = len(unique_words)
        print(f"La taille du vocabulaire est de {vocabulary_size} mots uniques.")
    
    except FileNotFoundError:
        print("Erreur : Le fichier spécifié n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_file>")
    else:
        calculate_vocabulary_size(sys.argv[1])

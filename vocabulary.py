import sys

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
        print(f"Nombre de lignes non vides : {non_empty_line_count}")
    
    except FileNotFoundError:
        print("Erreur : Le fichier spécifié n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_file>")
    else:
        count_non_empty_lines(sys.argv[1])

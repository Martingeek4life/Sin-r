import sys

def remove_empty_lines(input_file_path):
    # Déterminer le chemin du fichier de sortie
    output_file_path = input_file_path + "_no_empty_lines"

    try:
        # Ouvrir le fichier d'entrée en mode lecture et le fichier de sortie en mode écriture
        with open(input_file_path, 'r', encoding='utf-8') as file_in, \
             open(output_file_path, 'w', encoding='utf-8') as file_out:
            # Lire chaque ligne du fichier d'entrée
            line_number = 1
            for line in file_in:
                # Vérifier si la ligne est vide (en ignorant les espaces)
                if line.strip() == '':
                    print(f"Ligne vide trouvée à la ligne {line_number}")
                else:
                    # Écrire la ligne dans le fichier de sortie si elle n'est pas vide
                    file_out.write(line)
                line_number += 1
        print(f"Les lignes ont été traitées. Les lignes non vides ont été écrites dans '{output_file_path}'")
    except FileNotFoundError:
        print("Erreur : Le fichier spécifié n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture ou de l'écriture des fichiers: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_file>")
    else:
        remove_empty_lines(sys.argv[1])

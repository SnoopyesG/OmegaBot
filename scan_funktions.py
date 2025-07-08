import os
import ast

def list_functions_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

def scan_folder(folder):
    result = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    functions = list_functions_in_file(path)
                    result[path] = functions
                except Exception as e:
                    result[path] = [f"Fehler beim Lesen: {e}"]
    return result

if __name__ == "__main__":
    folder = "."  # aktueller Ordner, anpassen falls nötig
    funktionsliste = scan_folder(folder)
    for file, funcs in funktionsliste.items():
        print(f"{file}:")
        for f in funcs:
            print(f"  - {f}")
        print()

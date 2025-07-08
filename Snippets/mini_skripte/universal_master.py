import sys
from datetime import datetime

try:
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.panel import Panel
except ImportError:
    print("Installiere das Paket 'rich' zuerst mit: pip3 install rich")
    sys.exit(1)

# Log-Funktion
def log_output(text):
    with open("tool_log.txt", "a") as f:
        f.write(f"[{datetime.now()}] {text}\n")

console = Console()

def run_demo(name, func, desc=""):
    console.rule(f"[bold green]{name}[/bold green]")
    if desc:
        console.print(desc, style="cyan")
    try:
        func()
        log_output(f"{name}: erfolgreich ausgeführt.")
    except Exception as e:
        console.print(f"[red]Fehler:[/red] {e}")
        log_output(f"{name}: Fehler – {e}")
    console.print("\n[bold magenta]Zurück zum Menü mit Enter[/bold magenta]")
    input()

def check_module(modulename):
    try:
        __import__(modulename)
        return True
    except ImportError:
        return False

def main_menu():
    TOOLS = [
        ("CSV Exporter Demo", "Erstellt trades.csv mit Beispieldaten.", "csv_exporter_demo", "main"),
        ("Stickies Exporter Demo", "Zeigt Rohdaten der Stickies-App (Mac).", "stickies_exporter_demo", "main"),
        ("Simple GUI Demo", "Startet kleine grafische Oberfläche.", "simple_gui_demo", "main"),
        ("Trading Bot Demo", "Berechnet Indikatoren und simuliert Coin-Rotation.", "trading_bot_demo", "main"),
        ("ML Analyse", "Analysiert trades.csv mit Machine Learning.", "machine_learning_export_framework", "analyse_trades_ml"),
        ("Beenden", "Das Programm verlassen.", None, None)
    ]

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Snippet & Tool Tester[/bold cyan]", width=50))
        for idx, (title, desc, _, _) in enumerate(TOOLS, 1):
            console.print(f"[{idx}] {title} – [dim]{desc}[/dim]", style="yellow")
        try:
            choice = int(Prompt.ask("\n[green]Nummer eingeben[/green]"))
        except ValueError:
            continue
        if 1 <= choice <= len(TOOLS):
            title, desc, modul, func = TOOLS[choice-1]
            if modul is None:
                console.print("\n[bold red]Bye![/bold red]")
                sys.exit()
            # Check auf fehlendes Modul als Extra-Feature
            if not check_module(modul):
                console.print(f"[red]Modul '{modul}' nicht gefunden![/red] Bitte erst die passende Datei bereitstellen.")
                continue
            # Laden & ausführen
            run_demo(title, getattr(__import__(modul), func), desc)
        else:
            console.print("[red]Ungültige Auswahl![/red]")

if __name__ == "__main__":
    main_menu()

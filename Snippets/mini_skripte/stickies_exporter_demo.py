def main():
    import os
    stickies_path = os.path.expanduser('~/Library/StickiesDatabase')
    if os.path.exists(stickies_path):
        with open(stickies_path, 'rb') as f:
            data = f.read()
        print("Stickies-Rohdaten (gekürzt):", data[:200])
    else:
        print("Stickies-Datenbank nicht gefunden.")
if __name__ == "__main__":
    main()

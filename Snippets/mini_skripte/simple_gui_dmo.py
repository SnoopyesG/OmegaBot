"""
Datei: simple_gui_demo.py
Mini-Skript: Zeigt eine einfache GUI für den Start.
"""
import tkinter as tk

root = tk.Tk()
root.title("TradingBot Demo GUI")
tk.Label(root, text="Hallo TradingBot!").pack(padx=20, pady=20)
tk.Button(root, text="Beenden", command=root.destroy).pack()
root.mainloop()

import os

command = "cat workflow.txt"

if input(f"Vill du köra detta kommando: {command}? (ja/nej) ") == "ja":
    os.system(command)
    print("***kommandot har körts***")


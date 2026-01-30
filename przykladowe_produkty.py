"""
Skrypt dodający przykładowe produkty do bazy danych.
Uruchom raz, żeby wypełnić bazę podstawowymi produktami.
"""

from kalorie import init_db, dodaj_produkt

# Inicjalizacja bazy
init_db()

# Przykładowe produkty (wartości na 100g)
# Format: (nazwa, kalorie, białko, węglowodany, tłuszcze, kategoria)

produkty = [
    # Nabiał
    ("Jajko kurze", 155, 13.0, 1.1, 11.0, "nabiał"),
    ("Mleko 2%", 50, 3.4, 4.8, 2.0, "nabiał"),
    ("Ser żółty gouda", 356, 25.0, 2.2, 27.0, "nabiał"),
    ("Twaróg półtłusty", 119, 18.0, 4.0, 4.0, "nabiał"),
    ("Jogurt naturalny", 61, 5.0, 4.0, 3.0, "nabiał"),

    # Mięso
    ("Pierś z kurczaka", 110, 23.0, 0.0, 1.5, "mięso"),
    ("Pierś z indyka", 104, 24.0, 0.0, 1.0, "mięso"),
    ("Wołowina mielona", 250, 17.0, 0.0, 20.0, "mięso"),
    ("Schab wieprzowy", 157, 21.0, 0.0, 8.0, "mięso"),

    # Węglowodany
    ("Ryż biały ugotowany", 130, 2.7, 28.0, 0.3, "węglowodany"),
    ("Makaron ugotowany", 131, 5.0, 25.0, 1.0, "węglowodany"),
    ("Chleb pszenny", 265, 9.0, 49.0, 3.0, "węglowodany"),
    ("Chleb żytni", 215, 6.0, 46.0, 1.0, "węglowodany"),
    ("Ziemniaki gotowane", 77, 2.0, 17.0, 0.1, "węglowodany"),
    ("Płatki owsiane", 379, 13.0, 68.0, 6.5, "węglowodany"),

    # Warzywa
    ("Pomidor", 18, 0.9, 3.9, 0.2, "warzywa"),
    ("Ogórek", 15, 0.7, 3.6, 0.1, "warzywa"),
    ("Marchewka", 41, 0.9, 10.0, 0.2, "warzywa"),
    ("Brokuły", 34, 2.8, 7.0, 0.4, "warzywa"),
    ("Szpinak", 23, 2.9, 3.6, 0.4, "warzywa"),

    # Owoce
    ("Jabłko", 52, 0.3, 14.0, 0.2, "owoce"),
    ("Banan", 89, 1.1, 23.0, 0.3, "owoce"),
    ("Pomarańcza", 47, 0.9, 12.0, 0.1, "owoce"),

    # Tłuszcze
    ("Oliwa z oliwek", 884, 0.0, 0.0, 100.0, "tłuszcze"),
    ("Masło", 717, 0.9, 0.1, 81.0, "tłuszcze"),
    ("Orzechy włoskie", 654, 15.0, 14.0, 65.0, "tłuszcze"),
    ("Migdały", 579, 21.0, 22.0, 49.0, "tłuszcze"),
]

print("Dodawanie przykładowych produktów...\n")

for produkt in produkty:
    dodaj_produkt(*produkt)

print("\nGotowe! Możesz teraz uruchomić: python kalorie.py")

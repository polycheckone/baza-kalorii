"""
Prosta aplikacja do zarządzania bazą danych wartości kalorycznych produktów.
Baza SQLite z możliwością rozbudowy do aplikacji webowej.
"""

import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = Path(__file__).parent / "kalorie.db"


def get_connection():
    """Zwraca połączenie z bazą danych."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Inicjalizuje bazę danych - tworzy tabelę produktów jeśli nie istnieje."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produkty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nazwa TEXT NOT NULL UNIQUE,
            kalorie REAL NOT NULL,
            bialko REAL NOT NULL,
            weglowodany REAL NOT NULL,
            tluszcze REAL NOT NULL,
            kategoria TEXT,
            utworzono TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uzytkownicy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL UNIQUE,
            haslo TEXT NOT NULL,
            utworzono TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statystyki (
            klucz TEXT PRIMARY KEY,
            wartosc INTEGER DEFAULT 0
        )
    """)

    # Inicjalizuj licznik odwiedzin jeśli nie istnieje
    cursor.execute("INSERT OR IGNORE INTO statystyki (klucz, wartosc) VALUES ('odwiedziny', 0)")

    conn.commit()
    conn.close()
    print("Baza danych zainicjalizowana.")


def zwieksz_odwiedziny():
    """Zwiększa licznik odwiedzin o 1 i zwraca nową wartość."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE statystyki SET wartosc = wartosc + 1 WHERE klucz = 'odwiedziny'")
    cursor.execute("SELECT wartosc FROM statystyki WHERE klucz = 'odwiedziny'")
    wynik = cursor.fetchone()

    conn.commit()
    conn.close()

    return wynik[0] if wynik else 0


def pobierz_odwiedziny():
    """Pobiera aktualną liczbę odwiedzin."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT wartosc FROM statystyki WHERE klucz = 'odwiedziny'")
    wynik = cursor.fetchone()

    conn.close()

    return wynik[0] if wynik else 0


def dodaj_uzytkownika(login: str, haslo: str):
    """Dodaje nowego użytkownika do bazy danych."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        haslo_hash = generate_password_hash(haslo)
        cursor.execute("""
            INSERT INTO uzytkownicy (login, haslo)
            VALUES (?, ?)
        """, (login, haslo_hash))
        conn.commit()
        print(f"Dodano użytkownika: {login}")
    except sqlite3.IntegrityError:
        print(f"Użytkownik '{login}' już istnieje.")
    finally:
        conn.close()


def sprawdz_uzytkownika(login: str, haslo: str) -> bool:
    """Sprawdza dane logowania użytkownika."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT haslo FROM uzytkownicy WHERE login = ?", (login,))
    wynik = cursor.fetchone()
    conn.close()

    if not wynik:
        return False

    # Gość - puste hasło, logowanie bez hasła
    if wynik[0] == '' and haslo == '':
        return True

    # Normalny użytkownik - sprawdź hash hasła
    if wynik[0] and check_password_hash(wynik[0], haslo):
        return True

    return False


def dodaj_produkt(nazwa: str, kalorie: float, bialko: float, weglowodany: float, tluszcze: float, kategoria: str = None):
    """Dodaje nowy produkt do bazy danych."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO produkty (nazwa, kalorie, bialko, weglowodany, tluszcze, kategoria)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nazwa, kalorie, bialko, weglowodany, tluszcze, kategoria))
        conn.commit()
        print(f"Dodano produkt: {nazwa}")
    except sqlite3.IntegrityError:
        print(f"Produkt '{nazwa}' już istnieje w bazie.")
    finally:
        conn.close()


def lista_produktow(kategoria: str = None):
    """Wyświetla listę wszystkich produktów."""
    conn = get_connection()
    cursor = conn.cursor()

    if kategoria:
        cursor.execute("SELECT * FROM produkty WHERE kategoria = ? ORDER BY nazwa", (kategoria,))
    else:
        cursor.execute("SELECT * FROM produkty ORDER BY nazwa")

    produkty = cursor.fetchall()
    conn.close()

    if not produkty:
        print("Brak produktów w bazie.")
        return

    print(f"\n{'Nazwa':<30} {'kcal':>8} {'B':>8} {'W':>8} {'T':>8} {'Kategoria':<15}")
    print("-" * 85)

    for p in produkty:
        kategoria_str = p[6] if p[6] else "-"
        print(f"{p[1]:<30} {p[2]:>8.1f} {p[3]:>8.1f} {p[4]:>8.1f} {p[5]:>8.1f} {kategoria_str:<15}")

    print(f"\nRazem produktów: {len(produkty)}")


def szukaj_produkt(fraza: str):
    """Wyszukuje produkty po nazwie."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produkty WHERE nazwa LIKE ? ORDER BY nazwa", (f"%{fraza}%",))
    produkty = cursor.fetchall()
    conn.close()

    if not produkty:
        print(f"Nie znaleziono produktów zawierających '{fraza}'.")
        return

    print(f"\n{'Nazwa':<30} {'kcal':>8} {'B':>8} {'W':>8} {'T':>8}")
    print("-" * 70)

    for p in produkty:
        print(f"{p[1]:<30} {p[2]:>8.1f} {p[3]:>8.1f} {p[4]:>8.1f} {p[5]:>8.1f}")


def usun_produkt(nazwa: str):
    """Usuwa produkt z bazy danych."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM produkty WHERE nazwa = ?", (nazwa,))

    if cursor.rowcount > 0:
        print(f"Usunięto produkt: {nazwa}")
    else:
        print(f"Nie znaleziono produktu: {nazwa}")

    conn.commit()
    conn.close()


def oblicz_porcje(nazwa: str, gramy: float):
    """Oblicza wartości odżywcze dla podanej porcji produktu."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produkty WHERE nazwa = ?", (nazwa,))
    produkt = cursor.fetchone()
    conn.close()

    if not produkt:
        print(f"Nie znaleziono produktu: {nazwa}")
        return

    mnoznik = gramy / 100

    print(f"\n{produkt[1]} - {gramy}g:")
    print(f"  Kalorie:     {produkt[2] * mnoznik:.1f} kcal")
    print(f"  Białko:      {produkt[3] * mnoznik:.1f} g")
    print(f"  Węglowodany: {produkt[4] * mnoznik:.1f} g")
    print(f"  Tłuszcze:    {produkt[5] * mnoznik:.1f} g")


def menu_interaktywne():
    """Uruchamia interaktywne menu."""
    init_db()

    while True:
        print("\n=== BAZA KALORII ===")
        print("1. Lista produktów")
        print("2. Dodaj produkt")
        print("3. Szukaj produktu")
        print("4. Oblicz porcję")
        print("5. Usuń produkt")
        print("0. Wyjście")

        wybor = input("\nWybierz opcję: ").strip()

        if wybor == "1":
            lista_produktow()

        elif wybor == "2":
            print("\nDodawanie produktu (wartości na 100g):")
            nazwa = input("Nazwa: ").strip()
            try:
                kalorie = float(input("Kalorie (kcal): "))
                bialko = float(input("Białko (g): "))
                weglowodany = float(input("Węglowodany (g): "))
                tluszcze = float(input("Tłuszcze (g): "))
                kategoria = input("Kategoria (opcjonalnie): ").strip() or None
                dodaj_produkt(nazwa, kalorie, bialko, weglowodany, tluszcze, kategoria)
            except ValueError:
                print("Błąd: Wprowadź poprawne wartości liczbowe.")

        elif wybor == "3":
            fraza = input("Szukana fraza: ").strip()
            szukaj_produkt(fraza)

        elif wybor == "4":
            nazwa = input("Nazwa produktu: ").strip()
            try:
                gramy = float(input("Ilość (g): "))
                oblicz_porcje(nazwa, gramy)
            except ValueError:
                print("Błąd: Wprowadź poprawną wartość liczbową.")

        elif wybor == "5":
            nazwa = input("Nazwa produktu do usunięcia: ").strip()
            usun_produkt(nazwa)

        elif wybor == "0":
            print("Do widzenia!")
            break

        else:
            print("Nieznana opcja.")


if __name__ == "__main__":
    menu_interaktywne()

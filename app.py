"""
Aplikacja webowa do przeglądania wartości kalorycznych produktów.
"""

import os
import requests
from functools import wraps
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from kalorie import sprawdz_uzytkownika, init_db, get_connection

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Inicjalizuj bazę danych przy starcie
init_db()

# Lokalna baza podstawowych produktów (na 100g)
PRODUKTY_LOKALNE = [
    # Owoce
    {'id': 'lok_jablko', 'nazwa': 'Jabłko', 'kalorie': 52, 'bialko': 0.3, 'weglowodany': 14, 'tluszcze': 0.2},
    {'id': 'lok_banan', 'nazwa': 'Banan', 'kalorie': 89, 'bialko': 1.1, 'weglowodany': 23, 'tluszcze': 0.3},
    {'id': 'lok_pomarancza', 'nazwa': 'Pomarańcza', 'kalorie': 47, 'bialko': 0.9, 'weglowodany': 12, 'tluszcze': 0.1},
    {'id': 'lok_gruszka', 'nazwa': 'Gruszka', 'kalorie': 57, 'bialko': 0.4, 'weglowodany': 15, 'tluszcze': 0.1},
    {'id': 'lok_truskawka', 'nazwa': 'Truskawki', 'kalorie': 32, 'bialko': 0.7, 'weglowodany': 8, 'tluszcze': 0.3},
    {'id': 'lok_winogrono', 'nazwa': 'Winogrona', 'kalorie': 69, 'bialko': 0.7, 'weglowodany': 18, 'tluszcze': 0.2},
    {'id': 'lok_arbuz', 'nazwa': 'Arbuz', 'kalorie': 30, 'bialko': 0.6, 'weglowodany': 8, 'tluszcze': 0.2},
    {'id': 'lok_brzoskwinia', 'nazwa': 'Brzoskwinia', 'kalorie': 39, 'bialko': 0.9, 'weglowodany': 10, 'tluszcze': 0.3},
    {'id': 'lok_sliwka', 'nazwa': 'Śliwka', 'kalorie': 46, 'bialko': 0.7, 'weglowodany': 11, 'tluszcze': 0.3},
    {'id': 'lok_kiwi', 'nazwa': 'Kiwi', 'kalorie': 61, 'bialko': 1.1, 'weglowodany': 15, 'tluszcze': 0.5},
    {'id': 'lok_mandarynka', 'nazwa': 'Mandarynka', 'kalorie': 53, 'bialko': 0.8, 'weglowodany': 13, 'tluszcze': 0.3},
    {'id': 'lok_malina', 'nazwa': 'Maliny', 'kalorie': 52, 'bialko': 1.2, 'weglowodany': 12, 'tluszcze': 0.7},
    {'id': 'lok_borowka', 'nazwa': 'Borówki', 'kalorie': 57, 'bialko': 0.7, 'weglowodany': 14, 'tluszcze': 0.3},
    {'id': 'lok_wisnia', 'nazwa': 'Wiśnie', 'kalorie': 50, 'bialko': 1.0, 'weglowodany': 12, 'tluszcze': 0.3},
    {'id': 'lok_melon', 'nazwa': 'Melon', 'kalorie': 34, 'bialko': 0.8, 'weglowodany': 8, 'tluszcze': 0.2},
    {'id': 'lok_ananas', 'nazwa': 'Ananas', 'kalorie': 50, 'bialko': 0.5, 'weglowodany': 13, 'tluszcze': 0.1},
    {'id': 'lok_mango', 'nazwa': 'Mango', 'kalorie': 60, 'bialko': 0.8, 'weglowodany': 15, 'tluszcze': 0.4},
    {'id': 'lok_awokado', 'nazwa': 'Awokado', 'kalorie': 160, 'bialko': 2.0, 'weglowodany': 9, 'tluszcze': 15},
    {'id': 'lok_cytryna', 'nazwa': 'Cytryna', 'kalorie': 29, 'bialko': 1.1, 'weglowodany': 9, 'tluszcze': 0.3},
    {'id': 'lok_grejpfrut', 'nazwa': 'Grejpfrut', 'kalorie': 42, 'bialko': 0.8, 'weglowodany': 11, 'tluszcze': 0.1},

    # Warzywa
    {'id': 'lok_marchew', 'nazwa': 'Marchew', 'kalorie': 41, 'bialko': 0.9, 'weglowodany': 10, 'tluszcze': 0.2},
    {'id': 'lok_ziemniak', 'nazwa': 'Ziemniak', 'kalorie': 77, 'bialko': 2.0, 'weglowodany': 17, 'tluszcze': 0.1},
    {'id': 'lok_pomidor', 'nazwa': 'Pomidor', 'kalorie': 18, 'bialko': 0.9, 'weglowodany': 3.9, 'tluszcze': 0.2},
    {'id': 'lok_ogorek', 'nazwa': 'Ogórek', 'kalorie': 15, 'bialko': 0.7, 'weglowodany': 3.6, 'tluszcze': 0.1},
    {'id': 'lok_cebula', 'nazwa': 'Cebula', 'kalorie': 40, 'bialko': 1.1, 'weglowodany': 9, 'tluszcze': 0.1},
    {'id': 'lok_czosnek', 'nazwa': 'Czosnek', 'kalorie': 149, 'bialko': 6.4, 'weglowodany': 33, 'tluszcze': 0.5},
    {'id': 'lok_papryka', 'nazwa': 'Papryka', 'kalorie': 31, 'bialko': 1.0, 'weglowodany': 6, 'tluszcze': 0.3},
    {'id': 'lok_salata', 'nazwa': 'Sałata', 'kalorie': 15, 'bialko': 1.4, 'weglowodany': 2.9, 'tluszcze': 0.2},
    {'id': 'lok_kapusta', 'nazwa': 'Kapusta', 'kalorie': 25, 'bialko': 1.3, 'weglowodany': 6, 'tluszcze': 0.1},
    {'id': 'lok_brокuly', 'nazwa': 'Brokuły', 'kalorie': 34, 'bialko': 2.8, 'weglowodany': 7, 'tluszcze': 0.4},
    {'id': 'lok_kalafior', 'nazwa': 'Kalafior', 'kalorie': 25, 'bialko': 1.9, 'weglowodany': 5, 'tluszcze': 0.3},
    {'id': 'lok_szpinak', 'nazwa': 'Szpinak', 'kalorie': 23, 'bialko': 2.9, 'weglowodany': 3.6, 'tluszcze': 0.4},
    {'id': 'lok_burak', 'nazwa': 'Burak', 'kalorie': 43, 'bialko': 1.6, 'weglowodany': 10, 'tluszcze': 0.2},
    {'id': 'lok_cukinia', 'nazwa': 'Cukinia', 'kalorie': 17, 'bialko': 1.2, 'weglowodany': 3.1, 'tluszcze': 0.3},
    {'id': 'lok_baklazan', 'nazwa': 'Bakłażan', 'kalorie': 25, 'bialko': 1.0, 'weglowodany': 6, 'tluszcze': 0.2},
    {'id': 'lok_pieczarka', 'nazwa': 'Pieczarki', 'kalorie': 22, 'bialko': 3.1, 'weglowodany': 3.3, 'tluszcze': 0.3},
    {'id': 'lok_por', 'nazwa': 'Por', 'kalorie': 61, 'bialko': 1.5, 'weglowodany': 14, 'tluszcze': 0.3},
    {'id': 'lok_seler', 'nazwa': 'Seler', 'kalorie': 16, 'bialko': 0.7, 'weglowodany': 3, 'tluszcze': 0.2},
    {'id': 'lok_rzodkiewka', 'nazwa': 'Rzodkiewka', 'kalorie': 16, 'bialko': 0.7, 'weglowodany': 3.4, 'tluszcze': 0.1},
    {'id': 'lok_dynia', 'nazwa': 'Dynia', 'kalorie': 26, 'bialko': 1.0, 'weglowodany': 7, 'tluszcze': 0.1},

    # Mięso
    {'id': 'lok_kurczak_piersi', 'nazwa': 'Pierś z kurczaka', 'kalorie': 165, 'bialko': 31, 'weglowodany': 0, 'tluszcze': 3.6},
    {'id': 'lok_kurczak_udo', 'nazwa': 'Udo z kurczaka', 'kalorie': 209, 'bialko': 26, 'weglowodany': 0, 'tluszcze': 11},
    {'id': 'lok_wolowina', 'nazwa': 'Wołowina (chuda)', 'kalorie': 250, 'bialko': 26, 'weglowodany': 0, 'tluszcze': 15},
    {'id': 'lok_wieprzowina', 'nazwa': 'Wieprzowina (schab)', 'kalorie': 242, 'bialko': 27, 'weglowodany': 0, 'tluszcze': 14},
    {'id': 'lok_mieso_mielone', 'nazwa': 'Mięso mielone wołowe', 'kalorie': 254, 'bialko': 17, 'weglowodany': 0, 'tluszcze': 20},
    {'id': 'lok_indyk', 'nazwa': 'Indyk (pierś)', 'kalorie': 135, 'bialko': 30, 'weglowodany': 0, 'tluszcze': 1},
    {'id': 'lok_kaczka', 'nazwa': 'Kaczka', 'kalorie': 337, 'bialko': 19, 'weglowodany': 0, 'tluszcze': 28},
    {'id': 'lok_boczek', 'nazwa': 'Boczek', 'kalorie': 541, 'bialko': 37, 'weglowodany': 1.4, 'tluszcze': 42},
    {'id': 'lok_szynka', 'nazwa': 'Szynka', 'kalorie': 145, 'bialko': 21, 'weglowodany': 1.5, 'tluszcze': 6},
    {'id': 'lok_kielbasa', 'nazwa': 'Kiełbasa', 'kalorie': 301, 'bialko': 12, 'weglowodany': 2, 'tluszcze': 27},

    # Ryby
    {'id': 'lok_losos', 'nazwa': 'Łosoś', 'kalorie': 208, 'bialko': 20, 'weglowodany': 0, 'tluszcze': 13},
    {'id': 'lok_tunczyk', 'nazwa': 'Tuńczyk', 'kalorie': 132, 'bialko': 28, 'weglowodany': 0, 'tluszcze': 1},
    {'id': 'lok_dorsz', 'nazwa': 'Dorsz', 'kalorie': 82, 'bialko': 18, 'weglowodany': 0, 'tluszcze': 0.7},
    {'id': 'lok_pstrag', 'nazwa': 'Pstrąg', 'kalorie': 119, 'bialko': 20, 'weglowodany': 0, 'tluszcze': 3.5},
    {'id': 'lok_sledz', 'nazwa': 'Śledź', 'kalorie': 158, 'bialko': 18, 'weglowodany': 0, 'tluszcze': 9},
    {'id': 'lok_makrela', 'nazwa': 'Makrela', 'kalorie': 205, 'bialko': 19, 'weglowodany': 0, 'tluszcze': 14},
    {'id': 'lok_krewetki', 'nazwa': 'Krewetki', 'kalorie': 99, 'bialko': 24, 'weglowodany': 0.2, 'tluszcze': 0.3},

    # Nabiał
    {'id': 'lok_mleko', 'nazwa': 'Mleko 2%', 'kalorie': 50, 'bialko': 3.4, 'weglowodany': 4.8, 'tluszcze': 2},
    {'id': 'lok_mleko_pelne', 'nazwa': 'Mleko 3.2%', 'kalorie': 60, 'bialko': 3.2, 'weglowodany': 4.7, 'tluszcze': 3.2},
    {'id': 'lok_jogurt', 'nazwa': 'Jogurt naturalny', 'kalorie': 61, 'bialko': 3.5, 'weglowodany': 4.7, 'tluszcze': 3.3},
    {'id': 'lok_jogurt_grecki', 'nazwa': 'Jogurt grecki', 'kalorie': 97, 'bialko': 9, 'weglowodany': 3.6, 'tluszcze': 5},
    {'id': 'lok_ser_zolty', 'nazwa': 'Ser żółty (gouda)', 'kalorie': 356, 'bialko': 25, 'weglowodany': 2.2, 'tluszcze': 27},
    {'id': 'lok_ser_bialy', 'nazwa': 'Ser biały (twaróg)', 'kalorie': 98, 'bialko': 11, 'weglowodany': 3.4, 'tluszcze': 4.3},
    {'id': 'lok_ser_feta', 'nazwa': 'Ser feta', 'kalorie': 264, 'bialko': 14, 'weglowodany': 4.1, 'tluszcze': 21},
    {'id': 'lok_ser_mozzarella', 'nazwa': 'Mozzarella', 'kalorie': 280, 'bialko': 28, 'weglowodany': 3.1, 'tluszcze': 17},
    {'id': 'lok_maslo', 'nazwa': 'Masło', 'kalorie': 717, 'bialko': 0.9, 'weglowodany': 0.1, 'tluszcze': 81},
    {'id': 'lok_smietana', 'nazwa': 'Śmietana 18%', 'kalorie': 188, 'bialko': 2.6, 'weglowodany': 3.5, 'tluszcze': 18},
    {'id': 'lok_jajko', 'nazwa': 'Jajko kurze', 'kalorie': 155, 'bialko': 13, 'weglowodany': 1.1, 'tluszcze': 11},

    # Pieczywo i zboża
    {'id': 'lok_chleb_pszenny', 'nazwa': 'Chleb pszenny', 'kalorie': 265, 'bialko': 9, 'weglowodany': 49, 'tluszcze': 3.2},
    {'id': 'lok_chleb_zytni', 'nazwa': 'Chleb żytni', 'kalorie': 259, 'bialko': 8.5, 'weglowodany': 48, 'tluszcze': 3.3},
    {'id': 'lok_chleb_pelnoziarnisty', 'nazwa': 'Chleb pełnoziarnisty', 'kalorie': 247, 'bialko': 13, 'weglowodany': 41, 'tluszcze': 4.2},
    {'id': 'lok_bulka', 'nazwa': 'Bułka pszenna', 'kalorie': 276, 'bialko': 8, 'weglowodany': 53, 'tluszcze': 2.5},
    {'id': 'lok_ryz_bialy', 'nazwa': 'Ryż biały (gotowany)', 'kalorie': 130, 'bialko': 2.7, 'weglowodany': 28, 'tluszcze': 0.3},
    {'id': 'lok_ryz_brazowy', 'nazwa': 'Ryż brązowy (gotowany)', 'kalorie': 111, 'bialko': 2.6, 'weglowodany': 23, 'tluszcze': 0.9},
    {'id': 'lok_makaron', 'nazwa': 'Makaron (gotowany)', 'kalorie': 131, 'bialko': 5, 'weglowodany': 25, 'tluszcze': 1.1},
    {'id': 'lok_kasza_gryczana', 'nazwa': 'Kasza gryczana (gotowana)', 'kalorie': 92, 'bialko': 3.4, 'weglowodany': 20, 'tluszcze': 0.6},
    {'id': 'lok_kasza_jaglana', 'nazwa': 'Kasza jaglana (gotowana)', 'kalorie': 119, 'bialko': 3.5, 'weglowodany': 23, 'tluszcze': 1},
    {'id': 'lok_platki_owsiane', 'nazwa': 'Płatki owsiane', 'kalorie': 389, 'bialko': 17, 'weglowodany': 66, 'tluszcze': 7},
    {'id': 'lok_maka_pszenna', 'nazwa': 'Mąka pszenna', 'kalorie': 364, 'bialko': 10, 'weglowodany': 76, 'tluszcze': 1},

    # Tłuszcze i oleje
    {'id': 'lok_olej_rzepakowy', 'nazwa': 'Olej rzepakowy', 'kalorie': 884, 'bialko': 0, 'weglowodany': 0, 'tluszcze': 100},
    {'id': 'lok_oliwa', 'nazwa': 'Oliwa z oliwek', 'kalorie': 884, 'bialko': 0, 'weglowodany': 0, 'tluszcze': 100},
    {'id': 'lok_olej_slonecznikowy', 'nazwa': 'Olej słonecznikowy', 'kalorie': 884, 'bialko': 0, 'weglowodany': 0, 'tluszcze': 100},

    # Inne
    {'id': 'lok_miod', 'nazwa': 'Miód', 'kalorie': 304, 'bialko': 0.3, 'weglowodany': 82, 'tluszcze': 0},
    {'id': 'lok_cukier', 'nazwa': 'Cukier', 'kalorie': 387, 'bialko': 0, 'weglowodany': 100, 'tluszcze': 0},
    {'id': 'lok_czekolada', 'nazwa': 'Czekolada mleczna', 'kalorie': 535, 'bialko': 8, 'weglowodany': 59, 'tluszcze': 30},
    {'id': 'lok_orzechy_wloskie', 'nazwa': 'Orzechy włoskie', 'kalorie': 654, 'bialko': 15, 'weglowodany': 14, 'tluszcze': 65},
    {'id': 'lok_migdaly', 'nazwa': 'Migdały', 'kalorie': 579, 'bialko': 21, 'weglowodany': 22, 'tluszcze': 50},
    {'id': 'lok_orzeszki_ziemne', 'nazwa': 'Orzeszki ziemne', 'kalorie': 567, 'bialko': 26, 'weglowodany': 16, 'tluszcze': 49},
]


def wymaga_logowania(f):
    """Dekorator wymagający zalogowania."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'zalogowany' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Strona logowania."""
    if 'zalogowany' in session:
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        login_input = request.form.get('login', '')
        haslo = request.form.get('haslo', '')

        if sprawdz_uzytkownika(login_input, haslo):
            session['zalogowany'] = True
            session['uzytkownik'] = login_input
            session['jest_gosciem'] = (login_input == 'Gość')
            return redirect(url_for('index'))
        else:
            error = 'Nieprawidłowy login lub hasło'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Wylogowanie."""
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@wymaga_logowania
def index():
    """Strona główna."""
    return render_template('index.html',
                           uzytkownik=session.get('uzytkownik'),
                           jest_gosciem=session.get('jest_gosciem', False))


def usun_polskie_znaki(tekst):
    """Zamienia polskie znaki na łacińskie."""
    zamiana = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
        'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    for pl, lat in zamiana.items():
        tekst = tekst.replace(pl, lat)
    return tekst


def dodaj_polskie_znaki(tekst):
    """Próbuje dodać polskie znaki do tekstu (heurystyka)."""
    zamiana = {
        'a': 'ą', 'c': 'ć', 'e': 'ę', 'l': 'ł', 'n': 'ń',
        'o': 'ó', 's': 'ś', 'z': 'ż'
    }
    warianty = [tekst]
    # Generuj warianty z polskimi znakami
    for lat, pl in zamiana.items():
        if lat in tekst.lower():
            warianty.append(tekst.replace(lat, pl).replace(lat.upper(), pl.upper()))
    return warianty


def wyszukaj_w_api(query):
    """Wysyła zapytanie do Open Food Facts API."""
    url = 'https://pl.openfoodfacts.org/cgi/search.pl'
    params = {
        'search_terms': query,
        'search_simple': 1,
        'action': 'process',
        'json': 1,
        'page_size': 15,
        'fields': 'code,product_name,brands,nutriments'
    }
    response = requests.get(url, params=params, timeout=5)
    return response.json().get('products', [])


def wyszukaj_lokalne(query):
    """Wyszukuje w lokalnej liście produktów."""
    query_lower = usun_polskie_znaki(query.lower())
    wyniki = []
    for p in PRODUKTY_LOKALNE:
        nazwa_lower = usun_polskie_znaki(p['nazwa'].lower())
        if query_lower in nazwa_lower:
            wyniki.append(p.copy())
    return wyniki


def wyszukaj_w_bazie(query):
    """Wyszukuje w lokalnej bazie SQLite."""
    query_lower = f"%{query}%"
    query_bez_pl = f"%{usun_polskie_znaki(query)}%"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nazwa, kalorie, bialko, weglowodany, tluszcze
        FROM produkty
        WHERE nazwa LIKE ? OR nazwa LIKE ?
        LIMIT 20
    """, (query_lower, query_bez_pl))

    wyniki = []
    for row in cursor.fetchall():
        wyniki.append({
            'id': f'db_{row[0]}',
            'nazwa': row[1],
            'kalorie': row[2],
            'bialko': row[3],
            'weglowodany': row[4],
            'tluszcze': row[5]
        })

    conn.close()
    return wyniki


@app.route('/api/szukaj')
@wymaga_logowania
def szukaj_produkty():
    """Wyszukuje produkty w lokalnej bazie i Open Food Facts API."""
    query = request.args.get('q', '').strip()

    if not query or len(query) < 2:
        return jsonify([])

    wszystkie_produkty = []
    znalezione_nazwy = set()

    # 1. Szukaj w lokalnej liście (owoce, warzywa, mięso)
    for p in wyszukaj_lokalne(query):
        if p['nazwa'].lower() not in znalezione_nazwy:
            znalezione_nazwy.add(p['nazwa'].lower())
            p['zrodlo'] = 'lokalne'
            wszystkie_produkty.append(p)

    # 2. Szukaj w bazie SQLite (stare produkty użytkownika)
    for p in wyszukaj_w_bazie(query):
        if p['nazwa'].lower() not in znalezione_nazwy:
            znalezione_nazwy.add(p['nazwa'].lower())
            p['zrodlo'] = 'baza'
            wszystkie_produkty.append(p)

    # 3. Szukaj w Open Food Facts API
    try:
        zapytania = [query]
        query_bez_pl = usun_polskie_znaki(query)
        if query == query_bez_pl:
            warianty = {
                'jab': 'jabł', 'mie': 'mię', 'mas': 'masł',
                'zol': 'żół', 'ryz': 'ryż', 'ogor': 'ogór', 'miod': 'miód'
            }
            for klucz, wariant in warianty.items():
                if query.lower().startswith(klucz) and klucz != wariant:
                    zapytania.append(query.lower().replace(klucz, wariant))

        for q in zapytania[:2]:
            for product in wyszukaj_w_api(q):
                nazwa = product.get('product_name', '')
                if not nazwa or nazwa.lower() in znalezione_nazwy:
                    continue

                marka = product.get('brands', '')
                pelna_nazwa = f"{nazwa} ({marka})" if marka else nazwa

                if pelna_nazwa.lower() in znalezione_nazwy:
                    continue
                znalezione_nazwy.add(pelna_nazwa.lower())

                nutriments = product.get('nutriments', {})
                kalorie = nutriments.get('energy-kcal_100g') or nutriments.get('energy_100g', 0)
                if isinstance(kalorie, str):
                    kalorie = 0
                if kalorie > 900:
                    kalorie = kalorie / 4.184

                wszystkie_produkty.append({
                    'id': product.get('code', ''),
                    'nazwa': pelna_nazwa,
                    'kalorie': round(float(kalorie), 1),
                    'bialko': round(float(nutriments.get('proteins_100g', 0) or 0), 1),
                    'weglowodany': round(float(nutriments.get('carbohydrates_100g', 0) or 0), 1),
                    'tluszcze': round(float(nutriments.get('fat_100g', 0) or 0), 1),
                    'zrodlo': 'online'
                })

    except requests.RequestException:
        pass  # Kontynuuj z lokalnymi wynikami

    return jsonify(wszystkie_produkty[:25])


@app.route('/api/zapisz', methods=['POST'])
@wymaga_logowania
def zapisz_produkt():
    """Zapisuje produkt z internetu do lokalnej bazy."""
    data = request.json

    nazwa = data.get('nazwa', '').strip()
    if not nazwa:
        return jsonify({'error': 'Brak nazwy produktu'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO produkty (nazwa, kalorie, bialko, weglowodany, tluszcze, kategoria)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            nazwa,
            data.get('kalorie', 0),
            data.get('bialko', 0),
            data.get('weglowodany', 0),
            data.get('tluszcze', 0),
            'zapisane'
        ))
        conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'error': 'Produkt już istnieje lub błąd zapisu'}), 400
    finally:
        conn.close()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

"""
Aplikacja webowa do przeglądania wartości kalorycznych produktów.
"""

import os
from functools import wraps
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from kalorie import get_connection, sprawdz_uzytkownika, init_db, zwieksz_odwiedziny

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Inicjalizuj bazę danych przy starcie
init_db()


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
    # Zwiększ licznik odwiedzin
    odwiedziny = zwieksz_odwiedziny()

    return render_template('index.html',
                           uzytkownik=session.get('uzytkownik'),
                           jest_gosciem=session.get('jest_gosciem', False),
                           odwiedziny=odwiedziny)


@app.route('/api/produkty')
@wymaga_logowania
def get_produkty():
    """Zwraca wszystkie produkty pogrupowane według kategorii."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nazwa, kalorie, bialko, weglowodany, tluszcze, kategoria, jednostka
        FROM produkty
        ORDER BY kategoria, nazwa
    """)

    produkty = cursor.fetchall()
    conn.close()

    # Grupowanie według kategorii
    kategorie = {}
    for p in produkty:
        kat = p[6] if p[6] else "inne"
        if kat not in kategorie:
            kategorie[kat] = []
        kategorie[kat].append({
            'id': p[0],
            'nazwa': p[1],
            'kalorie': p[2],
            'bialko': p[3],
            'weglowodany': p[4],
            'tluszcze': p[5],
            'jednostka': p[7] if p[7] else 'g'
        })

    return jsonify(kategorie)


@app.route('/api/produkt/<int:id>')
def get_produkt(id):
    """Zwraca dane pojedynczego produktu."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nazwa, kalorie, bialko, weglowodany, tluszcze, kategoria
        FROM produkty WHERE id = ?
    """, (id,))

    p = cursor.fetchone()
    conn.close()

    if not p:
        return jsonify({'error': 'Nie znaleziono produktu'}), 404

    return jsonify({
        'id': p[0],
        'nazwa': p[1],
        'kalorie': p[2],
        'bialko': p[3],
        'weglowodany': p[4],
        'tluszcze': p[5],
        'kategoria': p[6]
    })


@app.route('/api/oblicz', methods=['POST'])
def oblicz_porcje():
    """Oblicza wartości dla podanej porcji."""
    data = request.json
    produkt_id = data.get('id')
    gramy = data.get('gramy', 100)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nazwa, kalorie, bialko, weglowodany, tluszcze
        FROM produkty WHERE id = ?
    """, (produkt_id,))

    p = cursor.fetchone()
    conn.close()

    if not p:
        return jsonify({'error': 'Nie znaleziono produktu'}), 404

    mnoznik = gramy / 100

    return jsonify({
        'nazwa': p[0],
        'gramy': gramy,
        'kalorie': round(p[1] * mnoznik, 1),
        'bialko': round(p[2] * mnoznik, 1),
        'weglowodany': round(p[3] * mnoznik, 1),
        'tluszcze': round(p[4] * mnoznik, 1)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

"""
Aplikacja webowa do przeglądania wartości kalorycznych produktów.
"""

from flask import Flask, render_template, jsonify, request
from kalorie import get_connection

app = Flask(__name__)


@app.route('/')
def index():
    """Strona główna."""
    return render_template('index.html')


@app.route('/api/produkty')
def get_produkty():
    """Zwraca wszystkie produkty pogrupowane według kategorii."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nazwa, kalorie, bialko, weglowodany, tluszcze, kategoria
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
            'tluszcze': p[5]
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
    app.run(debug=True, port=5000)

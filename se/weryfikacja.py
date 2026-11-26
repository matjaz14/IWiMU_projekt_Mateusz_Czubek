"""Weryfikacja bazy wiedzy (odpowiednik programu Cake z pakietu SPHINX) — do uzupełnienia na spotkaniu 3.
Uruchom: python se/weryfikacja.py wiedza/kawa_z_bledami.json
"""
import sys
from pathlib import Path

from silnik import OPERATORY, wczytaj_baze


def weryfikuj(baza):
    """Zwraca listę (poziom, komunikat); poziom to 'BŁĄD' albo 'UWAGA'."""
    raport = []
    atrybuty = baza["atrybuty"]
    reguly = baza["reguly"]

    # Test 1 (gotowy): powtórzone identyfikatory reguł
    ids = [r["id"] for r in reguly]
    for id_ in sorted({i for i in ids if ids.count(i) > 1}):
        raport.append(("BŁĄD", f"Powtórzony identyfikator reguły {id_}"))

    # Test 2 (gotowy): niezadeklarowane atrybuty i nieznane operatory w warunkach
    for r in reguly:
        for atr, op, wart in r["jesli"]:
            if atr not in atrybuty:
                raport.append(("BŁĄD", f"{r['id']}: niezadeklarowany atrybut '{atr}'"))
            if op not in OPERATORY:
                raport.append(("BŁĄD", f"{r['id']}: nieznany operator '{op}'"))

    # TODO 3: wartości spoza dziedziny — dla atrybutów z listą "wartosci"
    #         sprawdź warunki z operatorem == lub != (BŁĄD).

    for r in reguly:
        for atr,op, wart in r["jesli"]:
            if atr in atrybuty and "wartosci" in atrybuty[atr] and op in ("==", "!="):
                if wart not in atrybuty[atr]["wartosci"]:
                    raport.append(("BŁĄD", f"{r['id']}: wartość '{wart}' spoza dziedziny atrybutu '{atr}'"))
 

    # TODO 4: nieużywane atrybuty wejściowe (typ inny niż "wniosek", nieobecne w żadnym warunku)
    #         oraz nieużywane wartości atrybutów typu "wybor" (UWAGA).
    uzyte_atrybuty = {atr for r in reguly for atr, _, _ in r["jesli"]}
    for atr, opis in atrybuty.items():
        if opis["typ"] == "wniosek":
            continue
        if atr not in uzyte_atrybuty:
            raport.append(("UWAGA", f"Nieużywany atrybut wejściowy '{atr}'"))
            continue
        if opis["typ"] == "wybor":
            uzyte_wartosci = {wart for r in reguly for a, _, wart in r["jesli"] if a == atr}
            for wart in opis.get("wartosci", []):
                if wart not in uzyte_wartosci:
                    raport.append(("UWAGA", f"Nieużywana wartość '{wart}' atrybutu '{atr}'"))



    # TODO 5: warunek niemożliwy do spełnienia — warunek atr == wart, gdzie atr jest typu "wniosek",
    #         a żadna reguła nie ma wniosku ["atr", "wart"] (BŁĄD).
    wnioski =  {tuple(r["to"]) for r in reguly}
    for r in reguly:
        for atr, op, wart in r["jesli"]:
            if op == "==" and atr in atrybuty and atrybuty[atr]["typ"] == "wniosek":
                if (atr, wart) not in wnioski:
                     raport.append(("BŁĄD", f"{r['id']}: warunek '{atr} == {wart}' jest niemożliwy do spełnienia (żadna reguła nie wnioskuje tej wartości)"))

    # TODO 6: porównaj każdą parę reguł (warunki zamień na zbiory krotek: {tuple(w) for w in r["jesli"]}):
    #   - te same warunki i ten sam wniosek       -> duplikat (UWAGA)
    #   - te same warunki, inna wartość wniosku   -> sprzeczność (BŁĄD)
    #   - ten sam wniosek, warunki A ⊂ warunki B  -> B jest pochłaniana przez A (UWAGA)

    for i in range(len(reguly)):
        for j in range(i + 1, len(reguly)):
            a, b = reguly[i], reguly[j]
            war_a = {tuple(w) for w in a["jesli"]}
            war_b = {tuple(w) for w in b["jesli"]}
            if war_a == war_b:
                if a["to"] == b["to"]:
                    raport.append(("UWAGA", f"Reguły {a['id']} i {b['id']} są duplikatami"))
                elif a["to"][0] == b["to"][0]:
                    raport.append(("BŁĄD", f"Reguły {a['id']} i {b['id']} są sprzeczne (te same warunki, różny wniosek)"))
            elif a["to"] == b["to"]:
                if war_a < war_b:
                    raport.append(("UWAGA", f"Reguła {b['id']} jest pochłaniana przez {a['id']}"))
                elif war_b < war_a:
                    raport.append(("UWAGA", f"Reguła {a['id']} jest pochłaniana przez {b['id']}"))    


    # TODO 7: cel główny baza["cel"] musi być wnioskiem co najmniej jednej reguły (BŁĄD).
    if not any(r["to"][0] == baza["cel"] for r in reguly):
        raport.append(("BŁĄD", f"Cel '{baza['cel']}' nie jest wnioskiem żadnej reguły"))

    return raport


if __name__ == "__main__":
    plik = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent / "wiedza" / "kawa.json"
    wyniki = weryfikuj(wczytaj_baze(plik))
    if not wyniki:
        print("Baza wiedzy nie zawiera wykrytych problemów.")
    for poziom, komunikat in wyniki:
        print(f"[{poziom}] {komunikat}")
    print(f"\nZnaleziono: {len(wyniki)} (w kawa_z_bledami.json jest 10 problemów do wykrycia)")

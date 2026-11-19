"""Własne testy bazy FPL (Z2). Uruchom: python se/test_moja_dziedzina.py
(plik moja_dziedzina.json musi leżeć w wiedza/). Każdy przypadek sprawdza oba tryby."""
import copy
from pathlib import Path

from silnik import wczytaj_baze, wnioskuj_w_przod, wnioskuj_wstecz

baza = wczytaj_baze(Path(__file__).parent.parent / "wiedza" / "moja_dziedzina.json")

# Reguła konkurująca z R21: dla tych samych danych pasują obie. Wyjątek ekspercki:
# w podwójnej kolejce wykonawca karnych o wysokim potencjale to kapitan, a nie „differential”.
KONKURENT = {
    "id": "RK",
    "jesli": [["dostepnosc", "==", "dostępny"], ["liczba_meczow_w_kolejce", "==", "podwójna"],
              ["potencjal_punktowy", "==", "wysoki"], ["wykonawca_karnych", "==", "tak"]],
    "to": ["decyzja", "kapitan"],
    "metafora": "Podwójna kolejka i rzuty karne dają największą szansę na punkty, więc kapitan.",
    "coto": "Najlepszy wybór na kapitana: punkty tego zawodnika liczą się podwójnie.",
}


def z_konkurentem(przed_r21):
    """Kopia bazy z regułą RK przed albo po R21 (oryginalna baza się nie zmienia)."""
    kopia = copy.deepcopy(baza)
    i = [r["id"] for r in kopia["reguly"]].index("R21")
    kopia["reguly"].insert(i if przed_r21 else i + 1, KONKURENT)
    return kopia


DOSTEPNY = {"dostepnosc": "dostępny", "liczba_meczow_w_kolejce": "pojedyncza"}

# (nazwa, baza, dane wejściowe, oczekiwana decyzja, oczekiwany ślad w przód albo None)
PRZYPADKI = [
    ("typowy: differential", baza,
     {**DOSTEPNY, "forma_5": 7.2, "fdr_3": 2.0, "puchary_w_tygodniu": "nie", "minuty_3": 88, "posiadanie": 6},
     "differential", ["P1", "P5", "R13"]),
    ("typowy: kapitan (napastnik)", baza,
     {**DOSTEPNY, "forma_5": 9.0, "fdr_3": 1.5, "puchary_w_tygodniu": "nie", "minuty_3": 87, "posiadanie": 35,
      "wykonawca_karnych": "nie", "pozycja": "napastnik"},
     "kapitan", ["P1", "P5", "R15"]),
    # granica: forma_5 = 6 (>=), fdr_3 = 2,5 (<=), posiadanie = 10 (<=)
    ("granica: forma 6, FDR 2,5, posiadanie 10", baza,
     {**DOSTEPNY, "forma_5": 6, "fdr_3": 2.5, "puchary_w_tygodniu": "nie", "minuty_3": 71, "posiadanie": 10},
     "differential", ["P1", "P5", "R13"]),
    # granica: minuty_3 = 70 bez pucharów to jeszcze „niepewny” (reguła P6 ma <= 70)
    ("granica: minuty 70", baza,
     {**DOSTEPNY, "forma_5": 7, "fdr_3": 2, "puchary_w_tygodniu": "nie", "minuty_3": 70},
     "zostaw w składzie", ["P1", "P6", "R12"]),
    # brak wyniku: bez forma_5 nie da się ustalić potencjału punktowego, więc nie ma decyzji
    ("brak wyniku: nie znamy formy", baza,
     {**DOSTEPNY, "fdr_3": 2.0, "puchary_w_tygodniu": "nie", "minuty_3": 88, "posiadanie": 6},
     None, ["P5"]),
    # konflikt: pasują obie reguły, R21 i RK; wygrywa ta, która stoi wyżej
    ("konflikt: RK przed R21", z_konkurentem(True),
     {"dostepnosc": "dostępny", "liczba_meczow_w_kolejce": "podwójna", "forma_5": 8.0, "fdr_3": 2.2,
      "posiadanie": 4, "wykonawca_karnych": "tak"},
     "kapitan", ["P1", "RK"]),
    ("konflikt: RK po R21", z_konkurentem(False),
     {"dostepnosc": "dostępny", "liczba_meczow_w_kolejce": "podwójna", "forma_5": 8.0, "fdr_3": 2.2,
      "posiadanie": 4, "wykonawca_karnych": "tak"},
     "differential", ["P1", "R21"]),
]

ok = 0
for nazwa, b, wejscie, oczekiwane, oczekiwany_slad in PRZYPADKI:
    fakty, slad = wnioskuj_w_przod(b, wejscie)
    w_przod_ok = fakty.get("decyzja") == oczekiwane and (oczekiwany_slad is None or slad == oczekiwany_slad)

    zadane = []
    def zapytaj(atrybut, powod):
        zadane.append(atrybut)
        return wejscie.get(atrybut)            # brak danej = odpowiedź „nie wiem” (None)
    wstecz = wnioskuj_wstecz(b, "decyzja", {}, zapytaj, [])
    wstecz_ok = wstecz == oczekiwane and len(zadane) == len(set(zadane))

    status = "OK " if w_przod_ok and wstecz_ok else "BŁĄD"
    ok += w_przod_ok and wstecz_ok
    print(f"[{status}] {nazwa} -> w przód: {fakty.get('decyzja')} ({' -> '.join(slad)}), "
          f"wstecz: {wstecz}, pytań: {len(zadane)}")

print(f"\nZaliczone przypadki: {ok}/{len(PRZYPADKI)}")

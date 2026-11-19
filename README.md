# System doradczy w grze FPL: zarządzanie zawodnikiem ze składu (Z2)

## Konsultacja w trybie wstecz

```
> python se/silnik.py
=== Wnioskowanie w przód ===
Wynik: kapitan | reguły: P1 -> P5 -> R15

=== Wnioskowanie wstecz ===
Jaka jest dostępność zawodnika w najbliższej kolejce? (dostępny/wątpliwy/niedostępny) dostępny
Ile meczów gra drużyna zawodnika w najbliższej kolejce? (brak/pojedyncza/podwójna) pojedyncza
Jaka jest średnia punktów zawodnika z 5 ostatnich kolejek? 7
Jaka jest średnia trudność (FDR) 3 najbliższych meczów zawodnika (1–5)? 2
Czy drużyna zawodnika gra mecz pucharowy w tygodniu przed kolejką? (tak/nie) nie
Ile minut średnio zawodnik rozegrał w 3 ostatnich meczach? 88
Jakie jest posiadanie zawodnika wśród graczy FPL (%)? 12
Czy zawodnik wykonuje rzuty karne w swojej drużynie? (tak/nie) nie
Na jakiej pozycji gra zawodnik? (bramkarz/obrońca/pomocnik/napastnik) napastnik
Polecam: kapitan
Reguły: P1 -> P5 -> R15
```

**Dlaczego te pytania.** System zaczął od dostępności zawodnika i liczby meczów w kolejce, bo od tych danych zaczynają się wszystkie reguły decyzji. Żeby sprawdzić reguły z potencjałem punktowym i pewnością minut, musiał ustalić te wnioski, więc zapytał o formę i trudność terminarza (P1) oraz o puchary i średnie minuty (P5). Posiadanie (12%) przekroczyło próg 10, więc dopytał jeszcze o wykonawcę karnych i pozycję, bo tylko te dane rozróżniają reguły kapitana (R14–R18); nie zapytał natomiast o długość absencji ani szansę gry, ponieważ dotyczą tylko zawodników niedostępnych i wątpliwych.

## Kolejność reguł

Reguły decyzji w bazie wykluczają się wzajemnie (każda odpowiada jednej ścieżce drzewa), więc kolejność nie zmienia wyniku, ale ewentualną regułę wyjątku RK (kapitan dla wykonawcy karnych w podwójnej kolejce) należałoby postawić przed R21 (differential), ponieważ wykonawca karnych jest ważniejszym kandydatem na kapitana niż na zawodnika różnicującego.

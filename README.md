# Tema2SCD

Tema constă în implementarea unui API REST ce comunică cu o bază de date prin contracte formulate folosind protocolul HTTP. Pentru baza de date am folosit ```PostgressSql``` iar pentru aplicația de gestionare a bazei de date am folosit ```pgadmin```. Cele trei aplicații sunt pornite în interiorul unui ```docker```, fișierele pentru acesta găsindu-se în arhivă. 

Pentru a porni docker-ul și serviciile din el, se va folosi comanda
``docker compose -f tema2.yml up`` iar pentru închiderea lor ``docker compose -f tema2.yml down`` (poate și cu flag-ul ```-v``` în cazul în care se vrea un restart complet la baza de date).

## Baza de date

Baza de date conține trei tabele numite ```tari```, ```orase``` și ```temperaturi``` (desigur, fără diacritice). Baza de date este inițializată prin scriptul ```database.sql``` din folderul ```db```

### Tari
Tabela "Țări" conține 4 coloane:
- ID -> tipul de date este ```Serial```, fiind incrementat și adăugat automat de către baza de date la fiecare insert, fiind totodată și primary key
- NUME_TARA -> tip varchar, fiind unic per intrare
- LATITUDINE -> tip double
- LONGITUDINE -> tip double

### Orase
Tabela "Orașe" conține 5 coloane:
- ID -> la fel ca la "Țări", de tipul ```Serial``` și primary key
- ID_TARA -> tip int, fiind foreign key pentru tabela (se leagă la id-ul din Țări)
- NUME_ORAS -> tip varchar
- LATITUDINE -> tip double
- LONGITUDINE -> tip double
- Notă: perechea (ID_TARA și NUME_ORAS) este unică per intrare

### Temperaturi
Tabela "Temperaturi" conține 4 coloane:
- ID -> tip ```serial```, primary key
- ID_ORAS -> int, foreign key
- TIMESTAMP -> tip ```TIMESTAMP``` fiind setat să adauge automat ora la care a fost inserată intrarea în tabelă
- VALOARE -> tip float
- Perechea (ID_ORAS, TIMESTAMP) este unică per intrare

## Server.py

Aplicația ce primește cereri la adresa ```localhost:5000``` + ruta și face modificările cerute în baza de date. La bază este o aplicație în python ce folosește librăriile ```flask``` și ```psycopg2```, unde ```flask``` se ocupă de partea de ```REST```, iar ```psycopg2``` cu partea de interacțiune cu baza de date.

Modul prin care rulează aplicație este:
- Se conectează la baza de date prin intermediul variabilelor de mediu
- O dată ce primește o cerere, aceasta apelează funcția care se ocupă cu acea rută.
  - Dacă avem o cerere de tip ```POST```:
    - Întâi verificăm datele primite în request -> dacă sunt greșite => răspuns 400
    - Creăm query-ul de ```INSERT```
    - Trimitem query-ul prin ```db_cursor.execute(query)```
    - Dacă e introdus în baza de date => trimitem răspuns 201
    - Dacă nu e, înseamnă că am avut un conflict (încercăm să adaugăm ceva ce deja există în baza de date în cele mai multe cazuri) => răspuns 409
  - Dacă avem o cerere de tip ```GET```:
    - Verificăm în cazul în care aveam parametrii trimiți
    - Verificăm dacă avem vreun ```id``` trimis în rută
    - Creăm query-ul de ```SELECT``` în funcție de ce contrângeri avem
    - Îl trimitem la baza de data prin ```db_cursor```
    - Apelăm funcția specifică ce convertește datele primite din operația ```SELECT``` în format json.
  - Dacă avem o cerere de tip ```PUT``` 
    - Verificăm datele primite în request
    - Verificăm dacă id-ul dat în rută corespunde celui dat în request
    - Dacă nu sunt valide => răspuns 400
    - Verificăm dacă id-ul cerut există în baza de date
    - Dacă nu există => răspuns 404
    - Dacă există, facem query-ul de ```UPDATE``` și îl trimitem la baza de date
    - Dacă apar erori -> cel mai probabil modificând intrarea apare conflicte de date (ex: două țări cu același nume) => trimitem 409
    - Dacă nu, trimitem răspuns 200
  - Dacă avem o cerere de tip ```DELETE```
    - Verificăm dacă există intrarea în baza de date -> dacă nu => 404
    - Dacă da, trimitem query-ul de ```DELETE``` la baza de date și trimitem 200

## Pgadmin

Pentru accesarea aplicației de pgadmin rulată de docker, se accesează în browser URL-ul ```localhost:8000```, se introduce contul cu adresa ```admin@admin.com``` și parola ```admin```:
- Quick Links -> Add new server:
  - General -> name: orice aici
  - Connection:
    - Host name/address: ```db```
    - Port: 5432
    - Username: ```user```
    - Password: ```pass```
  
După acea se pot oberva întrările din baza de date, prin interacționarea cu baza de date numită ```user```, întrucât acolos sunt făcute tabelele
# Cardano Kebapizza – Backend (Shop + Admin in einem)

Ein Backend, aus dem alles zusammen laeuft: der Shop fuer Kunden, das
Admin-Panel und die API. Du brauchst nur einen Befehl und eine Adresse.

## Starten (das Einfachste)

Mac/Linux: im Ordner ein Terminal oeffnen und eingeben:

    ./start.sh

Windows: die Datei **start.bat** doppelklicken.

Das Skript richtet beim ersten Mal alles automatisch ein (Pakete, Datenbank,
Menue-Import, Admin-Zugang) und startet den Server. Beim naechsten Mal startet
es einfach nur.

Danach im Browser:

    Shop (Kunden):  http://127.0.0.1:8000/
    Admin-Panel:    http://127.0.0.1:8000/admin/

## Admin-Zugang

    Benutzer:  admin
    Passwort:  CardanoAdmin#2026

Bitte nach dem ersten Login aendern (oben rechts -> Passwort aendern).

## Tokens? Nein.

Du musst nichts mit Tokens oder Schluesseln machen.
- Admin-Panel: Benutzer + Passwort.
- Kunden: E-Mail + Passwort.
- Das Menue ist oeffentlich abrufbar.
Den Rest erledigt das Backend automatisch im Hintergrund.

## Was laeuft parallel?

Ein Server liefert gleichzeitig:
- den Shop unter „/" (Kunden bestellen hier)
- das Admin-Panel unter „/admin/"
- die API unter „/api/" (verbindet Shop und Backend)

Weil Shop und Backend dieselbe Adresse haben, verbindet sich der Shop von
selbst. Du musst nichts konfigurieren.

## Im Admin-Panel

- Bestellungen: Bestellnummer, Eingangszeit, Name, Telefon, Art (Lieferung/
  Abholung), Lieferadresse, alle Positionen, Wunschzeit, Trinkgeld,
  Liefergebuehr, enthaltene MwSt. (10 % Speisen/Ayran, 20 % Getraenke), Status.
- Menue verwalten: Kategorien und Artikel anlegen, Preise und Steuersatz aendern,
  Artikel auf „nicht verfuegbar" stellen, Reihenfolge festlegen. Aenderungen
  erscheinen sofort im Shop.


## Restaurantdaten (zentral im Admin)

Im Admin-Panel unter **Restaurantdaten** aenderst du an einer Stelle: Name,
Adresse, UID/Firmenbuch, Telefon, E-Mail, Oeffnungszeiten, Liefergebuehr,
Gratis-Lieferung-ab-Betrag und die Social-Media-Links. Diese Werte erscheinen
automatisch im Shop, auf der Startseite (Fusszeile, Kontakt, Social) und auf
dem Beleg (Firmenkopf, Liefergebuehr). Du musst nichts im Code aendern.

## Eigenes Admin-Dashboard

Unter **/manage/** gibt es ein einfaches, uebersichtliches Dashboard: Bestellungen
(mit Beleg-Druck), Speisekarte verwalten, Umsaetze nach Tag/Woche/Monat/Jahr
(druckbar fuer den Steuerberater) und alle Restaurantdaten. Login mit dem
Admin-Zugang. Details zum Online-Stellen stehen in DEPLOY.md.

## Spaeter online stellen

Lokal laeuft alles unter 127.0.0.1 (nur dein Rechner). Fuer den echten Betrieb
das Projekt bei einem Hoster laufen lassen, in der Datei `.env` einen langen
SECRET_KEY setzen und DEBUG=0. Dann ist der Shop unter deiner Domain erreichbar.

## API-Endpunkte (zur Info)

    GET  /api/menu/             Menue
    POST /api/orders/           Bestellung anlegen
    POST /api/auth/register/    Konto anlegen
    POST /api/auth/login/       Anmelden
    GET  /api/my-orders/        Eigene Bestellungen

Echte Social-Logins (Apple/Google/Facebook) brauchen zusaetzlich die jeweilige
OAuth-Anbindung. Anmeldung per E-Mail und Passwort funktioniert sofort.

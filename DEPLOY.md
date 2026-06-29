# Online stellen – Anleitung

Wichtig: GitHub Pages kann nur statische Seiten. Das Backend (Django) muss bei
einem Python-Hoster laufen. Es gibt zwei Wege.

## Weg A (empfohlen, am einfachsten): alles aus dem Backend

Das Backend liefert Shop, Admin-Dashboard und API gemeinsam aus. Du brauchst nur
einen Host und eine Adresse.

1. Lade den Ordner `cardano_backend` in ein GitHub-Repository.
2. Konto bei einem Hoster anlegen, z. B. Render (render.com) – kostenloser Plan
   reicht zum Start.
3. In Render: "New +" -> "Blueprint" -> dein Repository wählen. Render liest die
   beigelegte Datei `render.yaml` und richtet alles automatisch ein
   (Installation, Datenbank, Menue-Import, Admin-Zugang, Start).
4. Nach ein paar Minuten bekommst du eine Adresse wie
   `https://cardano-backend.onrender.com`. Damit:
   - Shop:            https://…onrender.com/
   - Admin-Dashboard: https://…onrender.com/manage/
   - Login:           admin / CardanoAdmin#2026  (bitte aendern!)

Fertig. Kunden bestellen im Shop, du verwaltest alles unter /manage/.

## Weg B: Seiten getrennt auf GitHub Pages, Backend separat

Wenn index, shop und admin als eigene GitHub-Pages-Repositorys laufen sollen:

1. Backend wie in Weg A hosten (du brauchst es in jedem Fall).
2. In jeder Seite oben im Code die Backend-Adresse eintragen:
   - shop.html:   `var BACKEND_URL = "https://…onrender.com";`
   - index.html:  `var BACKEND_URL = "https://…onrender.com";`
   - manage.html: `var BACKEND_URL = "https://…onrender.com";`
3. Im Backend die erlaubten Domains setzen (Render -> Environment):
   - `CORS_ALLOW_ALL = 0`
   - `CORS_ORIGINS = https://deinname.github.io`
   - `CSRF_TRUSTED  = https://deinname.github.io`
4. Seiten in die GitHub-Pages-Repos hochladen.

Hinweis: Weg A ist deutlich einfacher und ohne CORS-Themen. Empfehlung: erst mit
Weg A starten.

## Admin-Login

Das Admin-Dashboard ist die Datei `frontend/manage.html` und ist unter `/manage/`
erreichbar. Anmeldung mit dem Admin-Zugang (admin / CardanoAdmin#2026, bitte
aendern). Es ist kein Django-Wissen noetig.

## Online-Zahlung (Stripe) und Login mit Google – Stand

- Die Felder fuer Stripe (Schluessel) sind im Dashboard unter Restaurantdaten ->
  Zahlungen vorhanden. Damit echte Kartenzahlung laeuft, muss das Backend online
  sein (Weg A) und du brauchst ein Stripe-Konto mit deinen Schluesseln. Die
  eigentliche Zahlungsabwicklung (Stripe Checkout) richte ich dir ein, sobald das
  Backend online ist – dafuer ist die Live-Adresse noetig.
- Login mit Google/Apple/Facebook braucht ebenfalls das gehostete Backend und
  einen OAuth-Zugang beim jeweiligen Anbieter (z. B. Google Cloud). Sobald das
  Backend online ist und du den Google-Zugang angelegt hast, schalte ich es frei.
  Login per E-Mail und Passwort funktioniert schon jetzt.

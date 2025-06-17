# Backlogger

A web interface for tracking your backlog.  
Inspired by the Backlog project from [DarylTalksGames](https://www.youtube.com/@DarylTalksGames).

**Backend**
- FastAPI
- Psycopg
- howlongtobeatpy (for est_length)
- steam api for the names

**Database**
- PostgreSQL

**Frontend**
- Jinja2
- Tailwind (via CDN)
- htmx

You can use Docker Compose to run it locally.

## TODO:
- [ ] post finish site
- [ ] stats site
- [ ] game list
- [ ] login / auth
- [ ] profil section in index
- [ ] profil page
  - profil picture
  - reset password
  - name / username
  - email
- [ ] flesh out all sides
  - images
  - text

<br>

## Some Theoretical Questions (in German)

### Unterscheidung von REST zu anderen API-Spezifikationen wie SOAP

| REST          | SOAP              |
| ------------- | ----------------- |
| JSON oder XML | Nur XML           |
| flexible      | strikter Standard |
| http          | http, smtp, tcp   |

<br>

### Definition von RESTful (Was bedeutet REST?)

REST (Representational State Transfer)

Restful = Eine Programmierschnittstelle (API) den REST Prinzipien folgt

Prinzipien:
1. Client-Server: Trennung von Client und Server
2. Stateless: Server speichert keine Daten über Requests/Zustand
3. Cache: Antworten auf Abfragen können gecacht werden
4. Uniform Interface: Ressourcen sind klar geregelt
5. Layered System: Es ist möglich Zwischensysteme zwischen zu schalten

<br>

### Erläuterung des Protokolls auf dem REST basiert

Läuft über Http

Ein Client kann http Anfragen (Request) zu einem Server machen

Der Server verarbeitet diese Anfragen und liefert dann eine Antwort (Response) auf diese Anfrage zurück

Ein Request besteht aus einer URL und einer Methode. Zusätzlich kann noch ein Header und ein Body hinzugefügt werden

<br>

### Definition von CRUD (inkl. dem Zusammenhang zum verwendeten Protokoll)

C - Create - Ist die Request Methode POST

R - Read - GET

U - Update - PUT / PATCH

D - Delete - DELETE

Bildet die Grundlage für die meisten APIs und ist wie man in Restful APIs die Ressourcen behandelt

<br>

### Erläuterung der Request-Methoden und der Responses (inkl. Status-Codes)

GET - Ruft Ressourcen ab

POST - Erstellt neue Ressourcen

PUT - Eine Ressource wird komplett ersetzt

PATCH - Eine Ressource wird teilweise geändert

DELETE - Eine Ressource wird gelöscht

<br>

Es gibt viele unterschiedliche Status codes, aber es gibt ein paar die man eigentlich immer verwendet:

200 - OK - Anfrage war erfolgreich (Normal bei GET Requests, aber auch PUT und PATCH)

201 - Created - Passend zu POST, Eine Ressource wurde erstellt

204 - No Content - Erfolg, aber keine Rückgabe Inhalte

400 - Bad Request - Ungültige Request zum Beispiel Format

401 - Unauthorized - Authentifikation ist fehlgeschlagen oder fehlt

403 - Forbidden - Zugriff verboten

404 - Not Found - Ressource nicht gefunden

500 - Internal Server Error - Die Abfrage hat einen Fehler im Server hervorgebracht

<br>

### Erläuterung des Aufbaus von JSON und XML

**JSON**
Aufbau: Key-Value
Möglich Array und Verschachtelung zu nutzen
```JSON
{
  "key": "value",
  "someOther": 1,
  "help": [
    "send",
    "help"
  ],
  "POG": {
    "PEPEGA": "POGCHAMP"
  }
}
``` 
<br>

**XML**
Aufbau: Tags - öffnen und schließen

```XML
<test>
  <key>value</key>
  <help>send</help>
  <help>help</help>
  <POG>
    <PEPEGA>POGCHAMP</PEPEGA>
  </POG>
</test>
```

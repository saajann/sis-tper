SIS-TPER BOLOGNA 🚌📍

Sistema Informativo Segnalazione Fermate - Trasporto Passeggeri Emilia-Romagna
SIS-TPER Bologna è una web application interattiva progettata per permettere ai cittadini di segnalare e richiedere il posizionamento di nuove fermate dell'autobus nel territorio di Bologna. L'app combina la potenza della cartografia digitale con un'interfaccia intuitiva, ottimizzata per ogni tipo di dispositivo.

---------------------------------------------------------

🌐 ACCESSO AL SERVIZIO E SICUREZZA SSL

L'applicazione è raggiungibile attraverso due canali principali:

Dominio Principale: http://sistper.it (Accesso rapido via HTTP).

Mirror Sicuro (SSL): https://sis-tper.vercel.app/ (Versione con certificato di sicurezza SSL attivo).

---------------------------------------------------------

🔐 AREA AMMINISTRATIVA

L'accesso alla gestione delle segnalazioni è riservato al personale autorizzato ed è disponibile esclusivamente tramite connessione sicura al seguente indirizzo:

Pannello Admin: https://sis-tper.vercel.app/admin

---------------------------------------------------------

🌟 FUNZIONALITÀ PRINCIPALI

Mappa Interattiva: Visualizzazione geospaziale avanzata tramite Leaflet e Folium.

Gestione Livelli: Possibilità di attivare/disattivare la vista di linee bus, fermate esistenti, strade ed edifici direttamente dalla sidebar.

Filtri Dinamici: Sistema di filtraggio per visualizzare percorsi specifici selezionando una o più linee bus dalla lista.

Segnalazione Puntuale: Cliccando sulla mappa, l'utente posiziona un marker (trascinabile) per indicare il punto esatto della nuova fermata richiesta.

Form di Richiesta Avanzato:

Associazione della richiesta a una linea bus specifica.

Inserimento di note testuali (es. "vicino all'ingresso della scuola").

Definizione delle abitudini di utilizzo (giorni della settimana e fascia oraria preferita).

Interfaccia Mobile-First: Sidebar a scomparsa con menu "hamburger" per garantire la massima visibilità della mappa su smartphone e tablet.

---------------------------------------------------------

🛠️ STACK TECNOLOGICO

Backend: Python con framework Flask.

Frontend: HTML5, CSS3 (Custom Media Queries & Flexbox), JavaScript (ES6).

Cartografia: Folium (Python) e Leaflet.js (JavaScript).

Deployment: Vercel (per la versione HTTPS) e hosting dedicato per il dominio .it.

📁 STRUTTURA DEL PROGETTO (TREE)

├── app_logic/
│   ├── templates/
│   │   ├── admin_dashboard.html
│   │   ├── admin_login.html
│   │   └── index.html
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── map_utils.py
│   │   └── optimizer.py
│   ├── __init__.py
│   ├── admin_routes.py
│   ├── models.py
│   └── routes.py
├── data/
├── instance/
├── .gitignore
├── config.py
├── README.md
├── requirements.txt
├── run.py
└── vercel.json
---------------------------------------------------------

📱 OTTIMIZZAZIONE MOBILE E SIDEBAR

L'app è stata ottimizzata per essere utilizzata "sul campo":

Sidebar Dinamica: Su PC è possibile nascondere la barra laterale per una vista panoramica. Su smartphone, la barra diventa un overlay a scomparsa per non ostacolare la navigazione sulla mappa.

Precisione GPS: Grazie alla possibilità di trascinare il marker dopo il click, l'utente può correggere la posizione della segnalazione con estrema precisione.

Feedback Istantaneo: Un sistema di "Toast notifications" conferma all'utente l'invio corretto della richiesta al database.

---------------------------------------------------------

📝 MODALITÀ D'USO PER L'UTENTE

Apri il link sistper.it o la versione HTTPS.

Usa il tasto Menu per filtrare le linee bus di tuo interesse.

Clicca sulla mappa nel punto in cui vorresti la fermata.

Compila i dettagli nel pannello che apparirà in basso.

Clicca su Invia richiesta.

---------------------------------------------------------

⚖️ LICENZA

Progetto sviluppato per il miglioramento del trasporto pubblico locale (TPL) di Bologna.

---------------------------------------------------------

👥 AUTORI DEL PROGETTO

Il progetto SIS-TPER Bologna è stato ideato e sviluppato da:

- Daniele Primavera
- Saajan Saini
- Hartaj Singh
- Harwinder Singh

# Bella Nails & Lashes - Django Website

Ein professionelles Django-basiertes Website für ein Nagel- und Wimpernstudio in Deutschland.

## Features

- 🎨 **Modernes, responsives Design** - Optimiert für Desktop und Mobile
- 📅 **Intelligente Terminbuchung** - Automatische Verfügbarkeitsprüfung mit 3-Mitarbeiter-Limit
- 💅 **Umfangreiche Services** - 40+ verschiedene Nagel-, Wimpern- und Augenbrauenservices
- 📱 **Benutzerfreundlich** - Einfache Navigation und intuitive Bedienung
- 🖼️ **Galerie** - Showcase der schönsten Arbeiten
- 📝 **Blog-System** - Für Beauty-Tipps und Promotion
- 🇩🇪 **Deutsch lokalisiert** - Vollständig auf Deutsch verfügbar
- 👥 **Benutzerverwaltung** - Registrierung, Login, Profil-Management
- 📊 **Admin-Panel** - Vollständiges Django Admin für die Verwaltung

## Services

### Nagel-Services (22 Services)
- Maniküren (Classic, French, Gel, Express, Luxury Spa)
- Pediküren (Classic, Spa, Gel, Medical, Express)
- Nail Art & Extensions (Simple/Complex Art, Acryl, Gel Extensions)
- Spezialbehandlungen (Chrome, Ombre, Rhinestones)

### Wimpern-Services (12 Services)
- Wimpernverlängerung (Classic, Volume, Hybrid, Mega Volume)
- Wimpernbehandlungen (Lift, Tint, Lift + Tint)
- Maintenance & Removal

### Augenbrauen-Services (7 Services)
- Augenbrauenstyling (Shaping, Waxing, Threading)
- Augenbrauenbehandlungen (Tinting, Lamination, Henna, Microblading)

## Installation

### Voraussetzungen
- Python 3.8+
- pip
- virtualenv (empfohlen)

### Setup

1. **Repository klonen**
   ```bash
   git clone <repository-url>
   cd nails_salon
   ```

2. **Virtual Environment erstellen**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oder
   venv\\Scripts\\activate  # Windows
   ```

3. **Dependencies installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment-Variablen einrichten**
   ```bash
   cp .env.example .env
   # Bearbeiten Sie .env mit Ihren Einstellungen
   ```

5. **Datenbank migrieren**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Services-Daten laden**
   ```bash
   python manage.py populate_services
   ```

7. **Superuser erstellen**
   ```bash
   python manage.py createsuperuser
   ```

8. **Server starten**
   ```bash
   python manage.py runserver
   ```

Die Website ist nun unter `http://127.0.0.1:8000/` verfügbar.

## Projekt-Struktur

```
nails_salon/
├── manage.py
├── requirements.txt
├── README.md
├── nails_salon_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── salon/
│   ├── models.py          # Datenmodelle
│   ├── views.py           # View-Logik
│   ├── urls.py            # URL-Routing
│   ├── forms.py           # Formulare
│   ├── admin.py           # Admin-Konfiguration
│   └── management/
│       └── commands/
│           └── populate_services.py
├── templates/
│   ├── base.html
│   ├── salon/
│   └── registration/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/                 # Upload-Verzeichnis
```

## Terminbuchungs-System

Das Terminbuchungssystem berücksichtigt:
- **3-Mitarbeiter-Limit**: Maximal 3 gleichzeitige Termine pro Zeitslot
- **Geschäftszeiten**: Mo-Fr 9-18 Uhr, Sa 9-16 Uhr
- **Service-Dauer**: Automatische Berechnung von Zeitslots basierend auf Service-Dauer
- **Verfügbarkeitsprüfung**: Echtzeit-Überprüfung verfügbarer Zeiten
- **24h-Stornierungsregel**: Termine können bis 24h vorher storniert werden

## Admin-Panel

Zugriff über `/admin/` mit folgenden Funktionen:
- Service-Management (Kategorien, Services, Preise)
- Personal-Verwaltung (Staff, Verfügbarkeit, Spezialitäten)
- Terminverwaltung (Status, Zeiten, Kundendaten)
- Blog-System (Beiträge, Veröffentlichung)
- Galerie-Management (Bilder, Featured-Status)
- Bewertungs-Moderation

## Benutzer-Features

### Für Kunden:
- Online-Terminbuchung mit Verfügbarkeitsprüfung
- Benutzerregistrierung und -login
- Terminübersicht und -verwaltung
- Profil-Management
- Service-Katalog mit Filtern
- Bildergalerie
- Blog mit Beauty-Tipps

### Für Betreiber:
- Vollständiges Admin-Panel
- Terminkalender-Management
- Service- und Preispflege
- Content-Management (Blog, Galerie)
- Kundenverwaltung
- Bewertungs-System

## Technische Details

### Backend:
- **Django 4.2** - Web Framework
- **SQLite** - Datenbank (produktionsreif für PostgreSQL/MySQL)
- **Pillow** - Bildverarbeitung
- **django-crispy-forms** - Formular-Styling

### Frontend:
- **Bootstrap 5** - CSS Framework
- **Font Awesome** - Icons
- **Google Fonts** - Typografie
- **Responsive Design** - Mobile-optimiert

### Features:
- **AJAX** - Für dynamische Verfügbarkeitsprüfung
- **Image Upload** - Für Services, Personal, Galerie
- **Search** - Für Services und Blog-Beiträge
- **Pagination** - Für große Datenmengen
- **Form Validation** - Client- und serverseitig

## Deployment

Für Produktions-Deployment:
1. `DEBUG = False` in settings.py
2. Starker `SECRET_KEY`
3. Produktions-Datenbank (PostgreSQL empfohlen)
4. Static Files Serving (WhiteNoise oder CDN)
5. Media Files Storage (AWS S3 empfohlen)
6. Email-Konfiguration für Notifications

## Support

Bei Fragen oder Problemen:
- Überprüfen Sie die Django-Logs
- Stellen Sie sicher, dass alle Dependencies installiert sind
- Überprüfen Sie die Datenbank-Migrationen
- Kontaktieren Sie den Entwickler

## Lizenz

Dieses Projekt ist für den kommerziellen Einsatz in Nagel- und Beauty-Studios entwickelt worden.# lknails
# lknails

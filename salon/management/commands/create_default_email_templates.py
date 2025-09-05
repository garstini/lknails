from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from salon.models import EmailTemplate


class Command(BaseCommand):
    help = 'Create default email templates for the salon'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Erstelle Standard E-Mail Templates ===\n'))
        
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('❌ Kein Admin-Benutzer gefunden!'))
            self.stdout.write('Bitte erstellen Sie zuerst einen Superuser mit: python manage.py createsuperuser')
            return
        
        templates_created = 0
        
        # Default templates data
        default_templates = [
            {
                'name': 'Terminbestätigung Standard',
                'email_type': 'appointment_confirmation',
                'subject': 'Terminbestätigung - LK Nails & Lashes',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Terminbestätigung</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: {{background_color}}; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 10px; }
        .header { background: {{primary_color}}; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { padding: 20px; }
        .appointment-details { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }
        .btn { display: inline-block; background: {{primary_color}}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        {% if header_image %}
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="{{header_image}}" alt="LK Nails & Lashes" style="max-width: 200px;">
        </div>
        {% endif %}
        
        <div class="header">
            <h1>Terminbestätigung</h1>
        </div>
        
        <div class="content">
            <p>Liebe(r) <strong>{{customer_name}}</strong>,</p>
            
            <p>vielen Dank für Ihre Buchung! Hiermit bestätigen wir Ihren Termin bei LK Nails & Lashes.</p>
            
            <div class="appointment-details">
                <h3>📅 Termindetails:</h3>
                <p><strong>Datum:</strong> {{appointment_date}}</p>
                <p><strong>Uhrzeit:</strong> {{appointment_time}} Uhr</p>
                <p><strong>Services:</strong> {{appointment_services}}</p>
                <p><strong>Gesamtdauer:</strong> ca. {{total_duration}}</p>
                <p><strong>Gesamtpreis:</strong> {{total_price}} €</p>{% if staff_name %}
                <p><strong>Ihre Stylistin:</strong> {{staff_name}}</p>{% endif %}{% if appointment_notes %}
                <p><strong>Notizen:</strong> {{appointment_notes}}</p>{% endif %}
            </div>
            
            <p>Wir freuen uns sehr auf Ihren Besuch! Sollten Sie Fragen haben oder den Termin ändern müssen, zögern Sie nicht, uns zu kontaktieren.</p>
            
            <p><strong>Wichtige Hinweise:</strong></p>
            <ul>
                <li>Bitte kommen Sie 5 Minuten vor Ihrem Termin</li>
                <li>Bei Verspätung von mehr als 15 Minuten behalten wir uns vor, den Termin zu verkürzen oder abzusagen</li>
                <li>Absagen sind bis 24h vor dem Termin kostenfrei möglich</li>
            </ul>
        </div>
        
        <div class="footer">
            <p><strong>LK Nails & Lashes</strong><br>
            {{salon_address}}<br>
            Tel: {{salon_phone}}<br>
            E-Mail: {{customer_email}}</p>
            
            {% if footer_text %}
            <p>{{footer_text}}</p>
            {% endif %}
            
            <p>Mit freundlichen Grüßen,<br>Ihr LK Nails & Lashes Team</p>
        </div>
    </div>
</body>
</html>
                ''',
                'text_content': '''
Liebe(r) {{customer_name}},

vielen Dank für Ihre Buchung! Hiermit bestätigen wir Ihren Termin bei LK Nails & Lashes.

TERMINDETAILS:
Datum: {{appointment_date}}
Uhrzeit: {{appointment_time}} Uhr  
Services: {{appointment_services}}
Gesamtdauer: ca. {{total_duration}}
Gesamtpreis: {{total_price}} €
Ihre Stylistin: {{staff_name}}

Wir freuen uns sehr auf Ihren Besuch!

LK Nails & Lashes
{{salon_address}}
Tel: {{salon_phone}}
                ''',
                'is_active': True,
                'is_default': True,
                'primary_color': '#e91e63',
                'background_color': '#ffffff',
                'footer_text': 'Folgen Sie uns auf Instagram für die neuesten Trends und Angebote!'
            },
            {
                'name': 'Terminabsage Standard',
                'email_type': 'appointment_cancellation',
                'subject': 'Terminabsage - LK Nails & Lashes',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Terminabsage</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: {{background_color}}; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 10px; }
        .header { background: {{primary_color}}; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { padding: 20px; }
        .appointment-details { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }
        .btn { display: inline-block; background: {{primary_color}}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        {% if header_image %}
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="{{header_image}}" alt="LK Nails & Lashes" style="max-width: 200px;">
        </div>
        {% endif %}
        
        <div class="header">
            <h1>Terminabsage</h1>
        </div>
        
        <div class="content">
            <p>Liebe(r) <strong>{{customer_name}}</strong>,</p>
            
            <p>hiermit bestätigen wir die Absage Ihres Termins.</p>
            
            <div class="appointment-details">
                <h3>❌ Abgesagter Termin:</h3>
                <p><strong>Datum:</strong> {{appointment_date}}</p>
                <p><strong>Uhrzeit:</strong> {{appointment_time}} Uhr</p>
                <p><strong>Services:</strong> {{appointment_services}}</p>
                <p><strong>Preis:</strong> {{total_price}} €</p>
            </div>
            
            <p>Schade, dass wir Sie dieses Mal nicht bei uns begrüßen können. Gerne können Sie jederzeit einen neuen Termin buchen!</p>
            
            <p>Wir würden uns freuen, Sie bald wieder in unserem Salon begrüßen zu dürfen.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="#" class="btn">Neuen Termin buchen</a>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>LK Nails & Lashes</strong><br>
            {{salon_address}}<br>
            Tel: {{salon_phone}}</p>
            
            {% if footer_text %}
            <p>{{footer_text}}</p>
            {% endif %}
            
            <p>Mit freundlichen Grüßen,<br>Ihr LK Nails & Lashes Team</p>
        </div>
    </div>
</body>
</html>
                ''',
                'text_content': '''
Liebe(r) {{customer_name}},

hiermit bestätigen wir die Absage Ihres Termins.

ABGESAGTER TERMIN:
Datum: {{appointment_date}}
Uhrzeit: {{appointment_time}} Uhr  
Services: {{appointment_services}}
Preis: {{total_price}} €

Schade, dass wir Sie dieses Mal nicht bei uns begrüßen können. 
Gerne können Sie jederzeit einen neuen Termin buchen!

LK Nails & Lashes
{{salon_address}}
Tel: {{salon_phone}}
                ''',
                'is_active': True,
                'is_default': True,
                'primary_color': '#e91e63',
                'background_color': '#ffffff',
                'footer_text': 'Folgen Sie uns auf Instagram für die neuesten Trends und Angebote!'
            },
            {
                'name': 'Admin Benachrichtigung Standard',
                'email_type': 'admin_notification',
                'subject': '{{notification_type}} - {{customer_name}}',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{notification_type}}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; }
        .header { background: {{primary_color}}; color: white; padding: 15px; text-align: center; }
        .content { padding: 20px; }
        .details { background: #f8f9fa; padding: 15px; border-left: 4px solid {{primary_color}}; margin: 15px 0; }
        .urgent { background: #fff3cd; border-color: #ffc107; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🔔 {{notification_type}}</h2>
        </div>
        
        <div class="content">
            <p>Hallo {{admin_name}},</p>
            
            <p><strong>{{notification_type}}</strong> für einen Termin:</p>
            
            <div class="details">
                <h3>👤 Kundendetails:</h3>
                <p><strong>Name:</strong> {{customer_name}}</p>
                <p><strong>E-Mail:</strong> {{customer_email}}</p>
                <p><strong>Telefon:</strong> {{customer_phone}}</p>
            </div>
            
            <div class="details">
                <h3>📅 Termindetails:</h3>
                <p><strong>Datum:</strong> {{appointment_date}}</p>
                <p><strong>Uhrzeit:</strong> {{appointment_time}} Uhr</p>
                <p><strong>Services:</strong> {{appointment_services}}</p>
                <p><strong>Dauer:</strong> {{total_duration}}</p>
                <p><strong>Preis:</strong> {{total_price}} €</p>{% if staff_name %}
                <p><strong>Mitarbeiter:</strong> {{staff_name}}</p>{% endif %}{% if appointment_notes %}
                <p><strong>Notizen:</strong> {{appointment_notes}}</p>{% endif %}
            </div>
            
            <p>Bitte prüfen Sie den Kalender und bestätigen Sie den Termin falls erforderlich.</p>
        </div>
    </div>
</body>
</html>
                ''',
                'text_content': '''
{{notification_type}} - {{customer_name}}

Hallo {{admin_name}},

{{notification_type}} für einen Termin:

KUNDENDETAILS:
Name: {{customer_name}}
E-Mail: {{customer_email}}  
Telefon: {{customer_phone}}

TERMINDETAILS:
Datum: {{appointment_date}}
Uhrzeit: {{appointment_time}} Uhr
Services: {{appointment_services}}
Dauer: {{total_duration}}
Preis: {{total_price}} €

Bitte prüfen Sie den Kalender und bestätigen Sie den Termin falls erforderlich.
                ''',
                'is_active': True,
                'is_default': True,
                'primary_color': '#e91e63',
                'background_color': '#ffffff',
                'footer_text': 'LK Nails & Lashes Admin System'
            }
        ]
        
        # Create templates
        for template_data in default_templates:
            # Check if template already exists
            existing = EmailTemplate.objects.filter(
                email_type=template_data['email_type'],
                name=template_data['name']
            ).first()
            
            if existing:
                self.stdout.write(f'⏭️  Template "{template_data["name"]}" existiert bereits')
                continue
            
            # If this should be default, unset other defaults first
            if template_data.get('is_default'):
                EmailTemplate.objects.filter(
                    email_type=template_data['email_type'],
                    is_default=True
                ).update(is_default=False)
            
            # Create template
            template = EmailTemplate.objects.create(
                name=template_data['name'],
                email_type=template_data['email_type'],
                subject=template_data['subject'],
                html_content=template_data['html_content'],
                text_content=template_data['text_content'],
                is_active=template_data['is_active'],
                is_default=template_data['is_default'],
                primary_color=template_data['primary_color'],
                background_color=template_data['background_color'],
                footer_text=template_data['footer_text'],
                created_by=admin_user
            )
            
            templates_created += 1
            self.stdout.write(
                self.style.SUCCESS(f'✅ Template "{template.name}" erstellt ({template.email_type})')
            )
        
        self.stdout.write(f'\n🎉 {templates_created} Standard-Templates erfolgreich erstellt!')
        self.stdout.write('\n💡 Die Templates können jetzt im Admin-Panel angepasst werden.')
        self.stdout.write('💡 Verwenden Sie die Vorschau-Funktion, um die Templates zu testen.')
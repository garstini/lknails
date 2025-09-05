from django.core.management.base import BaseCommand
from django.core.mail import get_connection, EmailMessage
from salon.models import EmailConfiguration
import ssl
import smtplib


class Command(BaseCommand):
    help = 'Test email configuration and diagnose connection issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== E-Mail Konfiguration Test ===\n'))
        
        # Get active email configuration
        try:
            email_config = EmailConfiguration.objects.filter(is_active=True).first()
            if not email_config:
                self.stdout.write(self.style.ERROR('❌ Keine aktive E-Mail-Konfiguration gefunden!'))
                self.stdout.write('Bitte erstellen Sie eine E-Mail-Konfiguration im Admin-Panel.')
                return
            
            self.stdout.write(self.style.SUCCESS(f'✅ Aktive Konfiguration gefunden: {email_config.name}'))
            self.stdout.write(f'   SMTP Server: {email_config.smtp_server}:{email_config.smtp_port}')
            self.stdout.write(f'   Von E-Mail: {email_config.from_email}')
            self.stdout.write(f'   Benutzername: {email_config.smtp_username}')
            self.stdout.write(f'   TLS aktiviert: {email_config.use_tls}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Fehler beim Laden der Konfiguration: {e}'))
            return
            
        # Test SMTP connection
        self.stdout.write('\n--- SMTP Verbindungstest ---')
        try:
            if email_config.smtp_server == 'smtp.gmail.com':
                self.stdout.write('📧 Gmail SMTP wird verwendet')
                self.stdout.write('💡 Hinweis: Stellen Sie sicher, dass Sie ein App-Passwort verwenden!')
                self.stdout.write('💡 2-Faktor-Authentifizierung muss aktiviert sein')
            
            # Test connection manually
            server = smtplib.SMTP(email_config.smtp_server, email_config.smtp_port)
            server.ehlo()
            
            if email_config.use_tls:
                server.starttls()
                server.ehlo()
            
            server.login(email_config.smtp_username, email_config.smtp_password)
            server.quit()
            
            self.stdout.write(self.style.SUCCESS('✅ SMTP Verbindung erfolgreich!'))
            
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write(self.style.ERROR('❌ Authentifizierungsfehler!'))
            self.stdout.write(f'   Fehler: {e}')
            self.stdout.write('💡 Lösungsansätze:')
            self.stdout.write('   - Überprüfen Sie Benutzername und Passwort')
            self.stdout.write('   - Bei Gmail: Verwenden Sie ein App-Passwort')
            self.stdout.write('   - Aktivieren Sie 2-Faktor-Authentifizierung')
            return
            
        except smtplib.SMTPConnectError as e:
            self.stdout.write(self.style.ERROR('❌ Verbindungsfehler!'))
            self.stdout.write(f'   Fehler: {e}')
            self.stdout.write('💡 Lösungsansätze:')
            self.stdout.write('   - Überprüfen Sie Server und Port')
            self.stdout.write('   - Prüfen Sie Ihre Internetverbindung')
            self.stdout.write('   - Firewall-Einstellungen überprüfen')
            return
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Allgemeiner SMTP-Fehler: {e}'))
            self.stdout.write('💡 Connection unexpectedly closed kann bedeuten:')
            self.stdout.write('   - Falscher Port (587 für TLS, 465 für SSL)')
            self.stdout.write('   - TLS/SSL Konfiguration falsch')
            self.stdout.write('   - Server blockiert die Verbindung')
            return
        
        # Test sending email
        if options['to']:
            self.stdout.write('\n--- E-Mail Versandtest ---')
            try:
                connection = get_connection(
                    backend='django.core.mail.backends.smtp.EmailBackend',
                    host=email_config.smtp_server,
                    port=email_config.smtp_port,
                    username=email_config.smtp_username,
                    password=email_config.smtp_password,
                    use_tls=email_config.use_tls,
                )
                
                email = EmailMessage(
                    subject='✅ LK Nails & Lashes - E-Mail Test erfolgreich!',
                    body=f'''
Herzlichen Glückwunsch! 🎉

Ihre E-Mail-Konfiguration für LK Nails & Lashes funktioniert perfekt!

Konfigurationsdetails:
- SMTP Server: {email_config.smtp_server}:{email_config.smtp_port}
- Von: {email_config.from_email}
- TLS: {"Aktiviert" if email_config.use_tls else "Deaktiviert"}

Das E-Mail-System ist jetzt bereit für:
✅ Terminbestätigungen
✅ Terminabsagen
✅ Erinnerungen
✅ Admin-Benachrichtigungen

Mit freundlichen Grüßen,
Ihr LK Nails & Lashes Team
                    ''',
                    from_email=email_config.from_email,
                    to=[options['to']],
                    connection=connection,
                )
                
                email.send()
                self.stdout.write(self.style.SUCCESS(f'✅ Test-E-Mail erfolgreich an {options["to"]} gesendet!'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Fehler beim E-Mail-Versand: {e}'))
        
        else:
            self.stdout.write('\n💡 Für einen vollständigen Test verwenden Sie:')
            self.stdout.write('   python manage.py test_email_config --to ihre.email@example.com')
        
        # Gmail specific troubleshooting
        if email_config.smtp_server == 'smtp.gmail.com':
            self.stdout.write('\n=== Gmail Konfigurationshilfe ===')
            self.stdout.write('1. Google-Konto öffnen (myaccount.google.com)')
            self.stdout.write('2. Sicherheit → 2-Faktor-Authentifizierung aktivieren')
            self.stdout.write('3. App-Passwörter → Mail → Passwort generieren')
            self.stdout.write('4. Generiertes Passwort (nicht Google-Passwort!) verwenden')
            self.stdout.write('5. SMTP-Einstellungen:')
            self.stdout.write('   - Server: smtp.gmail.com')
            self.stdout.write('   - Port: 587')
            self.stdout.write('   - TLS: Aktiviert')
        
        self.stdout.write('\n🎯 E-Mail Konfigurationstest abgeschlossen!')
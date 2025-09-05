from django.core.management.base import BaseCommand
from salon.models import EmailTemplate


class Command(BaseCommand):
    help = 'Creates password reset email templates'

    def handle(self, *args, **options):
        # Password Reset Email Template
        password_reset_template, created = EmailTemplate.objects.get_or_create(
            name='password_reset',
            defaults={
                'subject': 'Passwort zurücksetzen - LK Nails & Lashes',
                'body': '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Passwort zurücksetzen - LK Nails & Lashes</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 40px 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 15px;
        }
        h1 {
            color: #e91e63;
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .content {
            color: #555;
            line-height: 1.6;
            font-size: 16px;
            margin-bottom: 30px;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #e91e63, #ad1457);
            color: white;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 16px;
            margin: 20px 0;
            text-align: center;
        }
        .button:hover {
            background: linear-gradient(135deg, #ad1457, #e91e63);
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            color: #888;
            font-size: 14px;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <img src="http://142.171.70.173/wordpress/wp-content/uploads/2024/09/zipwp-image-4128-scaled-300x300.jpg" alt="LK Nails & Lashes" class="logo">
            <h1>Passwort zurücksetzen</h1>
        </div>
        
        <div class="content">
            <p>Hallo,</p>
            <p>Sie haben eine Anfrage zum Zurücksetzen Ihres Passworts für Ihr LK Nails & Lashes Konto gestellt.</p>
            <p>Klicken Sie auf den unten stehenden Button, um ein neues Passwort zu erstellen:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{password_reset_url}}" class="button">Neues Passwort erstellen</a>
            </div>
            
            <div class="warning">
                <strong>⏰ Wichtiger Hinweis:</strong> Dieser Link ist nur für 24 Stunden gültig. Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail einfach.
            </div>
            
            <p>Falls der Button nicht funktioniert, kopieren Sie bitte den folgenden Link in Ihren Browser:</p>
            <p style="word-break: break-all; background: #f5f5f5; padding: 10px; border-radius: 5px; font-size: 14px;">
                {{password_reset_url}}
            </p>
            
            <p>Bei Fragen können Sie uns gerne kontaktieren:</p>
            <ul>
                <li>📧 E-Mail: lk.nails.lashes@gmail.com</li>
                <li>📞 Telefon: +49 30 80499718</li>
            </ul>
        </div>
        
        <div class="footer">
            <p><strong>LK Nails & Lashes</strong></p>
            <p>Hindenburgdamm 75, 12203 Berlin, Germany</p>
            <p>© 2025 LK Nails & Lashes. Alle Rechte vorbehalten.</p>
        </div>
    </div>
</body>
</html>''',
                'recipient_type': 'customer',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created password reset email template')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Password reset email template already exists')
            )
        
        self.stdout.write(self.style.SUCCESS('Password reset email template setup completed!'))
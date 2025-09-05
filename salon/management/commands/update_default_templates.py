from django.core.management.base import BaseCommand
from salon.models import EmailTemplate


class Command(BaseCommand):
    help = 'Update default email templates with detailed service information'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Cập nhật Templates với thông tin dịch vụ chi tiết ===\n'))
        
        # Update appointment confirmation template
        try:
            template = EmailTemplate.objects.get(
                email_type='appointment_confirmation',
                name='Terminbestätigung Standard'
            )
            
            # New template with detailed services
            new_html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Terminbestätigung</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: {{background_color}}; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: {{primary_color}}; color: white; padding: 30px 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .header h1 { margin: 0; font-size: 24px; }
        .content { padding: 30px; }
        .appointment-details { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid {{primary_color}}; }
        .services-section { background: #fff; border: 1px solid #e9ecef; border-radius: 8px; margin: 25px 0; overflow: hidden; }
        .services-header { background: {{primary_color}}; color: white; padding: 15px 20px; font-weight: bold; font-size: 16px; }
        .service-item { padding: 20px; border-bottom: 1px solid #e9ecef; display: flex; justify-content: space-between; align-items: flex-start; }
        .service-item:last-child { border-bottom: none; }
        .service-details { flex: 1; }
        .service-name { font-weight: bold; color: #333; font-size: 16px; margin-bottom: 8px; }
        .service-category { color: {{primary_color}}; font-size: 12px; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
        .service-description { color: #666; font-size: 14px; margin-bottom: 8px; }
        .service-duration { color: #888; font-size: 13px; }
        .service-price { font-weight: bold; color: {{primary_color}}; font-size: 18px; text-align: right; }
        .total-section { background: #f8f9fa; padding: 20px; margin: 25px 0; border-radius: 8px; text-align: center; }
        .total-price { font-size: 24px; font-weight: bold; color: {{primary_color}}; }
        .total-duration { color: #666; font-size: 14px; margin-top: 5px; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }
        .btn { display: inline-block; background: {{primary_color}}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        .contact-info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .important-notes { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .important-notes h4 { color: #856404; margin-top: 0; }
        .important-notes ul { margin: 10px 0; padding-left: 20px; }
        .important-notes li { margin-bottom: 5px; }
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
            <h1>✨ Terminbestätigung</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Vielen Dank für Ihre Buchung!</p>
        </div>
        
        <div class="content">
            <p style="font-size: 16px;">Liebe(r) <strong>{{customer_name}}</strong>,</p>
            
            <p>vielen Dank für Ihre Buchung! Hiermit bestätigen wir Ihren Termin bei <strong>LK Nails & Lashes</strong>.</p>
            
            <div class="appointment-details">
                <h3 style="margin-top: 0; color: {{primary_color}};">📅 Termindetails</h3>
                <p style="margin: 8px 0;"><strong>📅 Datum:</strong> {{appointment_date}}</p>
                <p style="margin: 8px 0;"><strong>🕐 Uhrzeit:</strong> {{appointment_time}} Uhr</p>
                {% if staff_name %}
                <p style="margin: 8px 0;"><strong>💅 Ihre Stylistin:</strong> {{staff_name}}</p>
                {% endif %}
                {% if appointment_notes %}
                <p style="margin: 8px 0;"><strong>📝 Notizen:</strong> {{appointment_notes}}</p>
                {% endif %}
            </div>
            
            <div class="services-section">
                <div class="services-header">
                    🛍️ Ihre gebuchten Services ({{services_count}} Services)
                </div>
                {% for service in services_details %}
                <div class="service-item">
                    <div class="service-details">
                        <div class="service-category">{{service.category}}</div>
                        <div class="service-name">{{service.name}}</div>
                        {% if service.description %}
                        <div class="service-description">{{service.description}}</div>
                        {% endif %}
                        <div class="service-duration">⏱️ {{service.duration}} Minuten</div>
                    </div>
                    <div class="service-price">{{service.price}} €</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="total-section">
                <div style="color: #666; font-size: 14px;">Gesamtsumme</div>
                <div class="total-price">{{total_price}} €</div>
                <div class="total-duration">Gesamtdauer: ca. {{total_duration}}</div>
            </div>
            
            <div class="important-notes">
                <h4>⚠️ Wichtige Hinweise</h4>
                <ul style="color: #856404;">
                    <li>Bitte kommen Sie 5 Minuten vor Ihrem Termin an</li>
                    <li>Bei Verspätung von mehr als 15 Minuten behalten wir uns vor, den Termin zu verkürzen oder abzusagen</li>
                    <li>Kostenlose Absagen sind bis 24 Stunden vor dem Termin möglich</li>
                    <li>Bringen Sie bitte ein gültiges Ausweisdokument mit</li>
                </ul>
            </div>
            
            <div class="contact-info">
                <h4 style="margin-top: 0; color: {{primary_color}};">📍 Salon Information</h4>
                <p style="margin: 8px 0;"><strong>{{salon_name}}</strong></p>
                <p style="margin: 8px 0;">📍 {{salon_address}}</p>
                <p style="margin: 8px 0;">📞 {{salon_phone}}</p>
                <p style="margin: 8px 0;">✉️ {{customer_email}}</p>
            </div>
            
            <p style="text-align: center; font-size: 16px; margin: 30px 0;">
                Wir freuen uns sehr auf Ihren Besuch! 💖
            </p>
        </div>
        
        <div class="footer">
            <p><strong>LK Nails & Lashes</strong></p>
            {% if footer_text %}
            <p>{{footer_text}}</p>
            {% endif %}
            <p style="margin-top: 15px;">Mit freundlichen Grüßen,<br>Ihr LK Nails & Lashes Team ✨</p>
        </div>
    </div>
</body>
</html>
            '''
            
            template.html_content = new_html_content
            template.save()
            
            self.stdout.write(self.style.SUCCESS('✅ Terminbestätigung Template cập nhật thành công'))
            
        except EmailTemplate.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Không tìm thấy template Terminbestätigung Standard'))
        
        # Update cancellation template
        try:
            cancel_template = EmailTemplate.objects.get(
                email_type='appointment_cancellation',
                name='Terminabsage Standard'
            )
            
            new_cancel_html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Terminabsage</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: {{background_color}}; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #dc3545; color: white; padding: 30px 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .header h1 { margin: 0; font-size: 24px; }
        .content { padding: 30px; }
        .appointment-details { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #dc3545; }
        .services-section { background: #fff; border: 1px solid #e9ecef; border-radius: 8px; margin: 25px 0; overflow: hidden; opacity: 0.7; }
        .services-header { background: #dc3545; color: white; padding: 15px 20px; font-weight: bold; font-size: 16px; }
        .service-item { padding: 20px; border-bottom: 1px solid #e9ecef; display: flex; justify-content: space-between; align-items: flex-start; }
        .service-item:last-child { border-bottom: none; }
        .service-details { flex: 1; }
        .service-name { font-weight: bold; color: #333; font-size: 16px; margin-bottom: 8px; }
        .service-category { color: #dc3545; font-size: 12px; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; }
        .service-description { color: #666; font-size: 14px; margin-bottom: 8px; }
        .service-duration { color: #888; font-size: 13px; }
        .service-price { font-weight: bold; color: #dc3545; font-size: 18px; text-align: right; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }
        .btn { display: inline-block; background: {{primary_color}}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }
        .cancelled-stamp { text-align: center; color: #dc3545; font-size: 18px; font-weight: bold; margin: 20px 0; padding: 10px; border: 2px solid #dc3545; border-radius: 5px; background: #f8d7da; }
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
            <h1>❌ Terminabsage</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Bestätigung der Terminabsage</p>
        </div>
        
        <div class="content">
            <p style="font-size: 16px;">Liebe(r) <strong>{{customer_name}}</strong>,</p>
            
            <p>hiermit bestätigen wir die Absage Ihres Termins bei <strong>LK Nails & Lashes</strong>.</p>
            
            <div class="cancelled-stamp">
                TERMIN ABGESAGT
            </div>
            
            <div class="appointment-details">
                <h3 style="margin-top: 0; color: #dc3545;">📅 Abgesagter Termin</h3>
                <p style="margin: 8px 0;"><strong>📅 Datum:</strong> {{appointment_date}}</p>
                <p style="margin: 8px 0;"><strong>🕐 Uhrzeit:</strong> {{appointment_time}} Uhr</p>
                {% if staff_name %}
                <p style="margin: 8px 0;"><strong>💅 Stylistin:</strong> {{staff_name}}</p>
                {% endif %}
            </div>
            
            <div class="services-section">
                <div class="services-header">
                    🛍️ Abgesagte Services ({{services_count}} Services)
                </div>
                {% for service in services_details %}
                <div class="service-item">
                    <div class="service-details">
                        <div class="service-category">{{service.category}}</div>
                        <div class="service-name">{{service.name}}</div>
                        {% if service.description %}
                        <div class="service-description">{{service.description}}</div>
                        {% endif %}
                        <div class="service-duration">⏱️ {{service.duration}} Minuten</div>
                    </div>
                    <div class="service-price">{{service.price}} €</div>
                </div>
                {% endfor %}
            </div>
            
            <p style="text-align: center; font-size: 16px; margin: 30px 0; color: #666;">
                Schade, dass wir Sie dieses Mal nicht bei uns begrüßen können. 😢
            </p>
            
            <div style="text-align: center; background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 5px; margin: 25px 0;">
                <h4 style="color: #155724; margin-top: 0;">Neuen Termin buchen? 🌟</h4>
                <p style="color: #155724; margin-bottom: 15px;">Wir würden uns freuen, Sie bald wieder in unserem Salon begrüßen zu dürfen!</p>
                <a href="#" class="btn">Jetzt neuen Termin buchen</a>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h4 style="margin-top: 0; color: {{primary_color}};">📞 Kontakt für neue Buchungen</h4>
                <p style="margin: 8px 0;">📞 {{salon_phone}}</p>
                <p style="margin: 8px 0;">📍 {{salon_address}}</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>LK Nails & Lashes</strong></p>
            {% if footer_text %}
            <p>{{footer_text}}</p>
            {% endif %}
            <p style="margin-top: 15px;">Mit freundlichen Grüßen,<br>Ihr LK Nails & Lashes Team ✨</p>
        </div>
    </div>
</body>
</html>
            '''
            
            cancel_template.html_content = new_cancel_html
            cancel_template.save()
            
            self.stdout.write(self.style.SUCCESS('✅ Terminabsage Template cập nhật thành công'))
            
        except EmailTemplate.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Không tìm thấy template Terminabsage Standard'))
        
        self.stdout.write('\n🎉 Tất cả templates đã được cập nhật với thông tin dịch vụ chi tiết!')
        self.stdout.write('💡 Giờ đây email xác nhận sẽ hiển thị:</p>')
        self.stdout.write('   - Chi tiết từng dịch vụ (tên, giá, thời gian, mô tả)')
        self.stdout.write('   - Danh mục dịch vụ')
        self.stdout.write('   - Tổng số dịch vụ')
        self.stdout.write('   - Layout đẹp và professional')
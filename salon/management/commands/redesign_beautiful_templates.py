from django.core.management.base import BaseCommand
from salon.models import EmailTemplate


class Command(BaseCommand):
    help = 'Redesign email templates with beautiful modern UI'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Thiết kế lại Email Templates với UI đẹp ===\n'))
        
        # Update appointment confirmation template with beautiful design
        try:
            template = EmailTemplate.objects.get(
                email_type='appointment_confirmation',
                name='Terminbestätigung Standard'
            )
            
            # Beautiful modern template design
            new_html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terminbestätigung - LK Nails & Lashes</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6; 
            color: #2c3e50; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .email-container { 
            max-width: 650px; 
            margin: 0 auto; 
            background: #ffffff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }
        
        /* Header Section */
        .header { 
            background: linear-gradient(135deg, {{primary_color}} 0%, #c44569 100%);
            color: white; 
            padding: 40px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 10px,
                rgba(255,255,255,0.03) 10px,
                rgba(255,255,255,0.03) 20px
            );
            animation: shimmer 3s linear infinite;
        }
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        .header-content { position: relative; z-index: 2; }
        .header h1 { 
            font-size: 28px; 
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header p { 
            font-size: 16px; 
            opacity: 0.95;
            font-weight: 300;
        }
        .confirmation-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 50px;
            margin-top: 15px;
            font-size: 14px;
            font-weight: 500;
        }
        
        /* Content Section */
        .content { 
            padding: 40px 30px;
        }
        .greeting {
            font-size: 18px;
            margin-bottom: 25px;
            color: #2c3e50;
        }
        .greeting strong {
            color: {{primary_color}};
        }
        
        /* Appointment Details Card */
        .appointment-card {
            background: linear-gradient(135deg, #f8f9ff 0%, #e8f4f8 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
            border: 1px solid rgba(102, 126, 234, 0.1);
            position: relative;
        }
        .appointment-card::before {
            content: '📅';
            position: absolute;
            top: -10px;
            left: 20px;
            background: white;
            padding: 0 10px;
            font-size: 20px;
        }
        .appointment-card h3 {
            color: {{primary_color}};
            margin: 0 0 20px 0;
            font-size: 18px;
            font-weight: 600;
        }
        .appointment-info {
            display: grid;
            gap: 12px;
        }
        .info-row {
            display: flex;
            align-items: center;
            padding: 8px 0;
        }
        .info-icon {
            width: 30px;
            font-size: 16px;
            margin-right: 15px;
        }
        .info-label {
            font-weight: 600;
            color: #34495e;
            width: 100px;
        }
        .info-value {
            color: #2c3e50;
            flex: 1;
        }
        
        /* Services Section */
        .services-container {
            background: #ffffff;
            border-radius: 15px;
            margin: 30px 0;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        }
        .services-header {
            background: linear-gradient(135deg, {{primary_color}} 0%, #667eea 100%);
            color: white;
            padding: 20px 25px;
            font-weight: 600;
            font-size: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .service-item {
            padding: 25px;
            border-bottom: 1px solid #f1f2f6;
            display: flex;
            gap: 20px;
            align-items: flex-start;
            transition: background-color 0.3s ease;
        }
        .service-item:last-child { border-bottom: none; }
        .service-item:hover { background: #f8f9ff; }
        
        .service-icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, {{primary_color}}, #667eea);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            font-weight: bold;
            flex-shrink: 0;
        }
        .service-details {
            flex: 1;
        }
        .service-category {
            color: {{primary_color}};
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        .service-name {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        .service-description {
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 10px;
            line-height: 1.5;
        }
        .service-duration {
            color: #95a5a6;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .service-price {
            font-size: 22px;
            font-weight: 700;
            color: {{primary_color}};
            text-align: right;
        }
        
        /* Total Section */
        .total-card {
            background: linear-gradient(135deg, #667eea 0%, {{primary_color}} 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin: 30px 0;
            position: relative;
            overflow: hidden;
        }
        .total-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='20' cy='20' r='20'/%3E%3C/g%3E%3C/svg%3E");
        }
        .total-content { position: relative; z-index: 2; }
        .total-label {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
            font-weight: 300;
        }
        .total-price {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .total-duration {
            font-size: 14px;
            opacity: 0.9;
            font-weight: 300;
        }
        
        /* Important Notes */
        .notes-card {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 1px solid #ffc107;
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
        }
        .notes-card h4 {
            color: #856404;
            margin-bottom: 15px;
            font-size: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .notes-list {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        .notes-list li {
            color: #856404;
            margin-bottom: 10px;
            padding-left: 25px;
            position: relative;
            font-size: 14px;
            line-height: 1.5;
        }
        .notes-list li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: #28a745;
            font-weight: bold;
        }
        
        /* Contact Info */
        .contact-card {
            background: linear-gradient(135deg, #f8f9ff 0%, #e8f4f8 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
        }
        .contact-card h4 {
            color: {{primary_color}};
            margin-bottom: 20px;
            font-size: 18px;
        }
        .contact-info {
            display: grid;
            gap: 10px;
            font-size: 14px;
        }
        .contact-info p {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin: 5px 0;
        }
        
        /* Footer */
        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #6c757d;
            font-size: 13px;
            line-height: 1.6;
        }
        .footer-logo {
            font-size: 18px;
            font-weight: 700;
            color: {{primary_color}};
            margin-bottom: 10px;
        }
        
        /* Responsive Design */
        @media (max-width: 600px) {
            .email-container { margin: 10px; border-radius: 15px; }
            .header, .content { padding: 25px 20px; }
            .service-item { flex-direction: column; gap: 15px; }
            .service-price { text-align: left; }
            .appointment-info { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="header-content">
                {% if header_image %}
                <img src="{{header_image}}" alt="LK Nails & Lashes" style="max-width: 120px; margin-bottom: 20px; border-radius: 10px;">
                {% endif %}
                <h1>✨ Terminbestätigung</h1>
                <p>Ihr Termin wurde erfolgreich bestätigt</p>
                <div class="confirmation-badge">
                    BESTÄTIGT ✓
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="greeting">
                Liebe(r) <strong>{{customer_name}}</strong>,
            </div>
            
            <p style="margin-bottom: 25px; color: #7f8c8d; font-size: 16px;">
                vielen Dank für Ihr Vertrauen! Wir freuen uns sehr auf Ihren Besuch bei <strong>LK Nails & Lashes</strong> und werden Ihnen ein unvergessliches Beauty-Erlebnis bieten.
            </p>
            
            <div class="appointment-card">
                <h3>Ihre Termindetails</h3>
                <div class="appointment-info">
                    <div class="info-row">
                        <div class="info-icon">📅</div>
                        <div class="info-label">Datum:</div>
                        <div class="info-value"><strong>{{appointment_date}}</strong></div>
                    </div>
                    <div class="info-row">
                        <div class="info-icon">🕐</div>
                        <div class="info-label">Uhrzeit:</div>
                        <div class="info-value"><strong>{{appointment_time}} Uhr</strong></div>
                    </div>
                    {% if staff_name %}
                    <div class="info-row">
                        <div class="info-icon">💅</div>
                        <div class="info-label">Stylistin:</div>
                        <div class="info-value"><strong>{{staff_name}}</strong></div>
                    </div>
                    {% endif %}
                    {% if appointment_notes %}
                    <div class="info-row">
                        <div class="info-icon">📝</div>
                        <div class="info-label">Notizen:</div>
                        <div class="info-value">{{appointment_notes}}</div>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <div class="services-container">
                <div class="services-header">
                    <span>💎</span>
                    <span>Ihre gebuchten Services ({{services_count}} Services)</span>
                </div>
                {% for service in services_details %}
                <div class="service-item">
                    <div class="service-icon">
                        {% if service.category == 'Nails' %}💅
                        {% elif service.category == 'Lashes' %}👁️
                        {% elif service.category == 'Brows' %}✨
                        {% else %}💆
                        {% endif %}
                    </div>
                    <div class="service-details">
                        <div class="service-category">{{service.category}}</div>
                        <div class="service-name">{{service.name}}</div>
                        {% if service.description %}
                        <div class="service-description">{{service.description}}</div>
                        {% endif %}
                        <div class="service-duration">
                            <span>⏱️</span>
                            <span>{{service.duration}} Minuten</span>
                        </div>
                    </div>
                    <div class="service-price">{{service.price}} €</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="total-card">
                <div class="total-content">
                    <div class="total-label">Gesamtsumme</div>
                    <div class="total-price">{{total_price}} €</div>
                    <div class="total-duration">Gesamtdauer: ca. {{total_duration}}</div>
                </div>
            </div>
            
            <div class="notes-card">
                <h4>
                    <span>⚠️</span>
                    <span>Wichtige Hinweise für Ihren Besuch</span>
                </h4>
                <ul class="notes-list">
                    <li>Bitte kommen Sie 5 Minuten vor Ihrem Termin an</li>
                    <li>Bei Verspätung über 15 Minuten wird der Termin möglicherweise verkürzt</li>
                    <li>Kostenlose Absagen sind bis 24 Stunden vorher möglich</li>
                    <li>Bringen Sie bitte ein gültiges Ausweisdokument mit</li>
                    <li>Für optimale Ergebnisse kommen Sie bitte ungeschminkt</li>
                </ul>
            </div>
            
            <div class="contact-card">
                <h4>📍 So finden Sie uns</h4>
                <div class="contact-info">
                    <p><strong>{{salon_name}}</strong></p>
                    <p><span>📍</span> {{salon_address}}</p>
                    <p><span>📞</span> {{salon_phone}}</p>
                    <p><span>✉️</span> Antwort an diese E-Mail</p>
                </div>
            </div>
            
            <div style="text-align: center; margin: 40px 0; font-size: 18px; color: {{primary_color}};">
                <strong>Wir freuen uns riesig auf Sie! 💖✨</strong>
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-logo">LK Nails & Lashes</div>
            <p>Ihr Premium Beauty Salon in Berlin</p>
            {% if footer_text %}
            <p style="margin-top: 15px;">{{footer_text}}</p>
            {% endif %}
            <p style="margin-top: 20px;">
                <strong>Mit freundlichen Grüßen,<br>
                Ihr LK Nails & Lashes Team ✨</strong>
            </p>
        </div>
    </div>
</body>
</html>
            '''
            
            template.html_content = new_html_content
            template.save()
            
            self.stdout.write(self.style.SUCCESS('✅ Email xác nhận đã được thiết kế lại với UI hiện đại'))
            
        except EmailTemplate.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Không tìm thấy template'))
        
        self.stdout.write('\n🎨 Template mới có những tính năng:')
        self.stdout.write('   ✨ Design hiện đại với gradient và animation')
        self.stdout.write('   📱 Responsive hoàn hảo trên mọi thiết bị') 
        self.stdout.write('   🎯 Icons và màu sắc phù hợp từng loại service')
        self.stdout.write('   💎 Layout card-based chuyên nghiệp')
        self.stdout.write('   🌟 Hiệu ứng hover và animation mượt mà')
        self.stdout.write('   📧 Tối ưu hiển thị trên mọi email client')
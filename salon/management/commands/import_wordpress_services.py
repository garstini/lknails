from django.core.management.base import BaseCommand
from salon.models import ServiceCategory, Service
from decimal import Decimal


class Command(BaseCommand):
    help = 'Import services from WordPress backup data'

    def handle(self, *args, **options):
        # Get or create categories
        nagel_category, _ = ServiceCategory.objects.get_or_create(
            name='Nägel',
            defaults={'description': 'Nagel-Services und Behandlungen'}
        )
        
        wimpern_category, _ = ServiceCategory.objects.get_or_create(
            name='Wimpern',
            defaults={'description': 'Wimpern-Services und Behandlungen'}
        )
        
        # Clear existing services
        Service.objects.all().delete()
        self.stdout.write('Cleared existing services')
        
        # WordPress services data
        services_data = [
            # Nägel-Pflege
            ('Maniküre ab', 'Nägel', 'Professionelle Nagelpflege', Decimal('15.00'), 15),
            ('Mit Shellac', 'Nägel', 'Nagelpflege mit Shellac-Lackierung', Decimal('25.00'), 25),
            ('Pediküre mit Massage', 'Nägel', 'Professionelle Fußpflege mit entspannender Massage', Decimal('25.00'), 25),
            ('Pediküre mit Shellac inkl. Massage', 'Nägel', 'Fußpflege mit Shellac und Massage', Decimal('35.00'), 35),
            ('Pediküre mit Acryl inkl. Massage', 'Nägel', 'Fußpflege mit Acryl-Verstärkung und Massage', Decimal('45.00'), 45),
            
            # Nägel-Flüssig Gel / Pulver-Gel - NEUMODELLAGE
            ('NEUMODELLAGE: Natur', 'Nägel', 'Natürliche Neumodellage mit Flüssig-Gel oder Pulver-Gel', Decimal('28.00'), 40),
            ('NEUMODELLAGE: mit Farbe', 'Nägel', 'Neumodellage mit Farbauftrag', Decimal('33.00'), 50),
            ('NEUMODELLAGE: Weiß / Babyboomer / Ombre / French / Glitzer', 'Nägel', 'Neumodellage mit speziellen Design-Techniken', Decimal('35.00'), 60),
            ('NEUMODELLAGE: Trend mit Farbe Babyboomer / Ombre / French / Glitzer', 'Nägel', 'Trendige Neumodellage mit Design-Elementen', Decimal('43.00'), 60),
            ('NEUMODELLAGE: Zehenmodellage oder Neu', 'Nägel', 'Neumodellage für Zehen', Decimal('40.00'), 60),
            
            # Nägel-Flüssig Gel / Pulver-Gel - AUFFÜLLEN
            ('AUFFÜLLEN: Natur', 'Nägel', 'Natürliches Auffüllen der Nägel', Decimal('25.00'), 40),
            ('AUFFÜLLEN: mit Farbe', 'Nägel', 'Auffüllen mit Farbauftrag', Decimal('30.00'), 45),
            ('AUFFÜLLEN: Weiß Babyboomer / Ombre / French / Glitzer', 'Nägel', 'Auffüllen mit Design-Techniken', Decimal('33.00'), 50),
            ('AUFFÜLLEN: Trend mit Farbe Babyboomer / Ombre / French / Glitzer', 'Nägel', 'Trendiges Auffüllen mit Design', Decimal('40.00'), 60),
            
            # Nägel-Design
            ('Überlänge', 'Nägel', 'Extra Länge für die Nägel', Decimal('3.00'), 10),
            ('Strass-Stein', 'Nägel', 'Dekoration mit Strass-Steinen', Decimal('0.50'), 10),
            
            # Wimpern-Classic 1:1
            ('Classic 1:1 - Neuset', 'Wimpern', 'Neue Classic Wimpernverlängerung 1:1', Decimal('55.00'), 60),
            ('Classic 1:1 - Auffüllen nach 2 Wochen', 'Wimpern', 'Auffüllen der Classic Wimpern nach 2 Wochen', Decimal('25.00'), 60),
            ('Classic 1:1 - Auffüllen nach 3 Wochen', 'Wimpern', 'Auffüllen der Classic Wimpern nach 3 Wochen', Decimal('30.00'), 60),
            ('Classic 1:1 - Auffüllen nach 4 Wochen', 'Wimpern', 'Auffüllen der Classic Wimpern nach 4 Wochen', Decimal('40.00'), 60),
            
            # Wimpern-Light Volume 2D-3D
            ('Light Volume 2D-3D - Neuset', 'Wimpern', 'Neue Light Volume Wimpernverlängerung 2D-3D', Decimal('69.00'), 90),
            ('Light Volume 2D-3D - Auffüllen nach 2 Wochen', 'Wimpern', 'Auffüllen der Light Volume Wimpern nach 2 Wochen', Decimal('30.00'), 60),
            ('Light Volume 2D-3D - Auffüllen nach 3 Wochen', 'Wimpern', 'Auffüllen der Light Volume Wimpern nach 3 Wochen', Decimal('35.00'), 60),
            ('Light Volume 2D-3D - Auffüllen nach 4 Wochen', 'Wimpern', 'Auffüllen der Light Volume Wimpern nach 4 Wochen', Decimal('40.00'), 60),
            
            # Wimpern-Volume 4D-5D
            ('Volume 4D-5D - Neuset', 'Wimpern', 'Neue Volume Wimpernverlängerung 4D-5D', Decimal('79.00'), 90),
            ('Volume 4D-5D - Auffüllen nach 2 Wochen', 'Wimpern', 'Auffüllen der Volume Wimpern nach 2 Wochen', Decimal('35.00'), 60),
            ('Volume 4D-5D - Auffüllen nach 3 Wochen', 'Wimpern', 'Auffüllen der Volume Wimpern nach 3 Wochen', Decimal('40.00'), 60),
            ('Volume 4D-5D - Auffüllen nach 4 Wochen', 'Wimpern', 'Auffüllen der Volume Wimpern nach 4 Wochen', Decimal('45.00'), 60),
            
            # Wimpern-Mega Volume ab 6D
            ('Mega Volume ab 6D - Neuset', 'Wimpern', 'Neue Mega Volume Wimpernverlängerung ab 6D', Decimal('99.00'), 120),
            ('Mega Volume ab 6D - Auffüllen nach 2 Wochen', 'Wimpern', 'Auffüllen der Mega Volume Wimpern nach 2 Wochen', Decimal('40.00'), 60),
            ('Mega Volume ab 6D - Auffüllen nach 3 Wochen', 'Wimpern', 'Auffüllen der Mega Volume Wimpern nach 3 Wochen', Decimal('45.00'), 60),
            ('Mega Volume ab 6D - Auffüllen nach 4 Wochen', 'Wimpern', 'Auffüllen der Mega Volume Wimpern nach 4 Wochen', Decimal('50.00'), 60),
            
            # Wimpern-Sonstiges
            ('Wimpernlifting', 'Wimpern', 'Natürliches Lifting der eigenen Wimpern', Decimal('35.00'), 10),
            ('Wimpern färben', 'Wimpern', 'Färbung der natürlichen Wimpern', Decimal('8.00'), 10),
            ('Augenbrauen zupfen & färben', 'Wimpern', 'Augenbrauen-Styling mit Zupfen und Färben', Decimal('17.00'), 10),
            ('Ablösen Wimpernverlängerung', 'Wimpern', 'Professionelles Entfernen der Wimpernverlängerung', Decimal('10.00'), 30),
        ]
        
        created_count = 0
        for name, category_name, description, price, duration in services_data:
            category = nagel_category if category_name == 'Nägel' else wimpern_category
            
            service, created = Service.objects.get_or_create(
                name=name,
                category=category,
                defaults={
                    'description': description,
                    'price': price,
                    'duration_minutes': duration,
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created: {name} - €{price} ({duration}min)')
            else:
                self.stdout.write(f'Updated: {name} - €{price} ({duration}min)')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {created_count} services')
        )
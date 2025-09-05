from django.core.management.base import BaseCommand
from salon.models import ServiceCategory, Service
from decimal import Decimal


class Command(BaseCommand):
    help = 'Update Wimpern services with proper hierarchical structure'

    def handle(self, *args, **options):
        # Get Wimpern category
        try:
            wimpern_category = ServiceCategory.objects.get(name='Wimpern')
        except ServiceCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('Wimpern category not found'))
            return
        
        # Clear existing Wimpern services
        Service.objects.filter(category=wimpern_category).delete()
        self.stdout.write('Cleared existing Wimpern services')
        
        # Hierarchical Wimpern services structure
        wimpern_services = [
            # Classic 1:1
            {
                'subcategory': 'Classic 1:1',
                'services': [
                    ('Neuset', 'Neue Classic Wimpernverlängerung 1:1', Decimal('55.00'), 60),
                    ('Auffüllen nach 2 Wochen', 'Auffüllen der Classic Wimpern nach 2 Wochen', Decimal('25.00'), 60),
                    ('Auffüllen nach 3 Wochen', 'Auffüllen der Classic Wimpern nach 3 Wochen', Decimal('30.00'), 60),
                    ('Auffüllen nach 4 Wochen', 'Auffüllen der Classic Wimpern nach 4 Wochen', Decimal('40.00'), 60),
                ]
            },
            
            # Light Volume 2D-3D
            {
                'subcategory': 'Light Volume 2D-3D',
                'services': [
                    ('Neuset', 'Neue Light Volume Wimpernverlängerung 2D-3D', Decimal('69.00'), 90),
                    ('Auffüllen nach 2 Wochen', 'Auffüllen der Light Volume Wimpern nach 2 Wochen', Decimal('30.00'), 60),
                    ('Auffüllen nach 3 Wochen', 'Auffüllen der Light Volume Wimpern nach 3 Wochen', Decimal('35.00'), 60),
                    ('Auffüllen nach 4 Wochen', 'Auffüllen der Light Volume Wimpern nach 4 Wochen', Decimal('40.00'), 60),
                ]
            },
            
            # Volume 4D-5D
            {
                'subcategory': 'Volume 4D-5D',
                'services': [
                    ('Neuset', 'Neue Volume Wimpernverlängerung 4D-5D', Decimal('79.00'), 90),
                    ('Auffüllen nach 2 Wochen', 'Auffüllen der Volume Wimpern nach 2 Wochen', Decimal('35.00'), 60),
                    ('Auffüllen nach 3 Wochen', 'Auffüllen der Volume Wimpern nach 3 Wochen', Decimal('40.00'), 60),
                    ('Auffüllen nach 4 Wochen', 'Auffüllen der Volume Wimpern nach 4 Wochen', Decimal('45.00'), 60),
                ]
            },
            
            # Mega Volume ab 6D
            {
                'subcategory': 'Mega Volume ab 6D',
                'services': [
                    ('Neuset', 'Neue Mega Volume Wimpernverlängerung ab 6D', Decimal('99.00'), 120),
                    ('Auffüllen nach 2 Wochen', 'Auffüllen der Mega Volume Wimpern nach 2 Wochen', Decimal('40.00'), 60),
                    ('Auffüllen nach 3 Wochen', 'Auffüllen der Mega Volume Wimpern nach 3 Wochen', Decimal('45.00'), 60),
                    ('Auffüllen nach 4 Wochen', 'Auffüllen der Mega Volume Wimpern nach 4 Wochen', Decimal('50.00'), 60),
                ]
            },
            
            # Sonstiges
            {
                'subcategory': 'Sonstiges',
                'services': [
                    ('Wimpernlifting', 'Natürliches Lifting der eigenen Wimpern', Decimal('35.00'), 45),
                    ('Wimpern färben', 'Färbung der natürlichen Wimpern', Decimal('8.00'), 15),
                    ('Augenbrauen zupfen & färben', 'Augenbrauen-Styling mit Zupfen und Färben', Decimal('17.00'), 20),
                    ('Ablösen Wimpernverlängerung', 'Professionelles Entfernen der Wimpernverlängerung', Decimal('10.00'), 30),
                ]
            }
        ]
        
        created_count = 0
        for subcategory_data in wimpern_services:
            subcategory_name = subcategory_data['subcategory']
            
            self.stdout.write(f'\n=== {subcategory_name} ===')
            
            for name, description, price, duration in subcategory_data['services']:
                service, created = Service.objects.get_or_create(
                    name=name,
                    category=wimpern_category,
                    subcategory=subcategory_name,
                    defaults={
                        'description': description,
                        'price': price,
                        'duration_minutes': duration,
                        'is_active': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  + {name} - €{price} ({duration}min)')
                else:
                    self.stdout.write(f'  ≈ {name} - €{price} ({duration}min)')
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} Wimpern services with subcategories')
        )
from django.core.management.base import BaseCommand
from salon.models import Service, ServiceCategory
from decimal import Decimal

class Command(BaseCommand):
    help = 'Update services based on LK Nails & Lashes website menu'

    def handle(self, *args, **options):
        # Clear existing services
        Service.objects.all().delete()
        ServiceCategory.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Cleared existing services and categories'))
        
        # Create categories
        nails_category = ServiceCategory.objects.create(
            name="Nägel",
            description="Professionelle Nagelpflege und Design"
        )
        
        lashes_category = ServiceCategory.objects.create(
            name="Wimpern",
            description="Professionelle Wimpernverlängerung"
        )
        
        special_category = ServiceCategory.objects.create(
            name="Spezialbehandlungen", 
            description="Exklusive Beauty-Behandlungen"
        )
        
        # Nail services based on the website
        nail_services = [
            # Basic Care
            {
                'name': 'Maniküre Classic',
                'description': 'Professionelle Nagelpflege mit Schneiden, Feilen und Pflege der Nagelhaut',
                'price': Decimal('25.00'),
                'duration': 45
            },
            {
                'name': 'Pediküre Classic', 
                'description': 'Umfassende Fußpflege mit Nagelpflege und Hornhautentfernung',
                'price': Decimal('35.00'),
                'duration': 60
            },
            
            # Gel Services  
            {
                'name': 'Gel Maniküre Neumodellage',
                'description': 'Komplette Neumodellage mit Flüssig Gel oder Pulver-Gel',
                'price': Decimal('45.00'),
                'duration': 90
            },
            {
                'name': 'Gel Maniküre Auffüllen', 
                'description': 'Auffüllen und Nachpflege bestehender Gel-Nägel',
                'price': Decimal('35.00'),
                'duration': 60
            },
            {
                'name': 'Gel Pediküre Neumodellage',
                'description': 'Komplette Neumodellage der Fußnägel mit Gel',
                'price': Decimal('50.00'),
                'duration': 100
            },
            {
                'name': 'Gel Pediküre Auffüllen',
                'description': 'Auffüllen und Pflege der Gel-Fußnägel', 
                'price': Decimal('40.00'),
                'duration': 70
            },
            
            # Design Services
            {
                'name': 'Nail Art Design Basic',
                'description': 'Einfaches Nageldesign mit Farben und Mustern',
                'price': Decimal('15.00'),
                'duration': 30
            },
            {
                'name': 'Nail Art Design Premium',
                'description': 'Aufwendiges Nageldesign mit speziellen Techniken',
                'price': Decimal('25.00'),
                'duration': 45
            },
            {
                'name': 'French Maniküre',
                'description': 'Klassische französische Maniküre',
                'price': Decimal('30.00'), 
                'duration': 50
            },
            {
                'name': 'Ombre Nails',
                'description': 'Moderner Farbverlauf auf den Nägeln',
                'price': Decimal('35.00'),
                'duration': 60
            },
            
            # Nail Extensions
            {
                'name': 'Nagelverlängerung mit Schablone',
                'description': 'Verlängerung der Nägel mit Gel und Schablone',
                'price': Decimal('55.00'),
                'duration': 120
            },
            {
                'name': 'Nagelverlängerung mit Tips',
                'description': 'Verlängerung der Nägel mit Kunstnägel-Tips',
                'price': Decimal('50.00'),
                'duration': 110
            }
        ]
        
        # Lash services based on the website
        lash_services = [
            {
                'name': 'Classic Lashes 1:1',
                'description': 'Klassische Wimpernverlängerung - eine Verlängerung pro Naturwimper',
                'price': Decimal('80.00'),
                'duration': 120
            },
            {
                'name': 'Light Volume 2D-3D',
                'description': 'Sanftes Volumen mit 2-3 dünnen Wimpern pro Naturwimper', 
                'price': Decimal('95.00'),
                'duration': 150
            },
            {
                'name': 'Volume 4D-5D',
                'description': 'Voluminöse Wimpern mit 4-5 Verlängerungen pro Naturwimper',
                'price': Decimal('110.00'),
                'duration': 180
            },
            {
                'name': 'Mega Volume ab 6D',
                'description': 'Maximum Volume mit 6+ ultrafeinen Wimpern pro Naturwimper',
                'price': Decimal('130.00'),
                'duration': 200
            },
            {
                'name': 'Wimpern Refill 2-3 Wochen',
                'description': 'Auffüllen der Wimpernverlängerung nach 2-3 Wochen',
                'price': Decimal('55.00'),
                'duration': 90
            },
            {
                'name': 'Wimpern Refill 4+ Wochen', 
                'description': 'Auffüllen der Wimpernverlängerung nach 4+ Wochen',
                'price': Decimal('75.00'),
                'duration': 120
            },
            {
                'name': 'Wimpernlifting',
                'description': 'Natürliche Wimpern dauerhaft nach oben biegen',
                'price': Decimal('45.00'),
                'duration': 60
            },
            {
                'name': 'Wimpernlifting + Färbung',
                'description': 'Wimpernlifting kombiniert mit Wimpernfärbung',
                'price': Decimal('55.00'),
                'duration': 75
            },
            {
                'name': 'Wimpern Entfernung',
                'description': 'Schonende Entfernung der Wimpernverlängerung',
                'price': Decimal('25.00'),
                'duration': 45
            }
        ]
        
        # Special services
        special_services = [
            {
                'name': 'Paraffin-Behandlung Hände',
                'description': 'Verwöhnen Sie Ihre Hände mit einer entspannenden Paraffin-Behandlung für geschmeidige Haut',
                'price': Decimal('20.00'),
                'duration': 30
            },
            {
                'name': 'Paraffin-Behandlung Füße',
                'description': 'Entspannende Paraffin-Behandlung für weiche und gepflegte Füße',
                'price': Decimal('25.00'),
                'duration': 35
            },
            {
                'name': 'Augenbrauen Styling',
                'description': 'Professionelles Augenbrauen-Styling mit Zupfen und Formen',
                'price': Decimal('15.00'),
                'duration': 25
            },
            {
                'name': 'Augenbrauen Färbung',
                'description': 'Färbung der Augenbrauen für einen ausdrucksvollen Blick',
                'price': Decimal('12.00'),
                'duration': 20
            },
            {
                'name': 'Beauty-Paket Complete',
                'description': 'Komplettpaket: Maniküre, Pediküre und Augenbrauen-Styling',
                'price': Decimal('85.00'),
                'duration': 150
            }
        ]
        
        # Create nail services
        for service_data in nail_services:
            Service.objects.create(
                name=service_data['name'],
                category=nails_category,
                description=service_data['description'],
                price=service_data['price'],
                duration_minutes=service_data['duration'],
                is_active=True
            )
            
        # Create lash services  
        for service_data in lash_services:
            Service.objects.create(
                name=service_data['name'],
                category=lashes_category,
                description=service_data['description'],
                price=service_data['price'],
                duration_minutes=service_data['duration'],
                is_active=True
            )
            
        # Create special services
        for service_data in special_services:
            Service.objects.create(
                name=service_data['name'],
                category=special_category,
                description=service_data['description'],
                price=service_data['price'],
                duration_minutes=service_data['duration'],
                is_active=True
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(nail_services)} nail services, '
                f'{len(lash_services)} lash services, and '
                f'{len(special_services)} special services based on LK Nails & Lashes website!'
            )
        )
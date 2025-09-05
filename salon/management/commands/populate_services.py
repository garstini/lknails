from django.core.management.base import BaseCommand
from salon.models import ServiceCategory, Service


class Command(BaseCommand):
    help = 'Populate the database with nail and lash services'

    def handle(self, *args, **options):
        self.stdout.write('Creating service categories and services...')
        
        # Create categories
        nail_category, _ = ServiceCategory.objects.get_or_create(
            name="Nails",
            defaults={
                'description': 'Professional nail services including manicures, pedicures, and nail art'
            }
        )
        
        lash_category, _ = ServiceCategory.objects.get_or_create(
            name="Lashes",
            defaults={
                'description': 'Eyelash extensions and treatments for beautiful, long lashes'
            }
        )
        
        eyebrow_category, _ = ServiceCategory.objects.get_or_create(
            name="Eyebrows",
            defaults={
                'description': 'Eyebrow shaping, tinting and microblading services'
            }
        )
        
        # Nail Services
        nail_services = [
            # Basic Manicures
            ("Classic Manicure", "Traditional manicure with nail shaping, cuticle care, and polish", 25.00, 45),
            ("French Manicure", "Classic French tips with nude base and white tips", 30.00, 60),
            ("Gel Manicure", "Long-lasting gel polish manicure", 35.00, 60),
            ("Express Manicure", "Quick nail shape, buff and polish", 20.00, 30),
            ("Luxury Spa Manicure", "Premium treatment with hand massage and moisturizing mask", 45.00, 75),
            
            # Pedicures
            ("Classic Pedicure", "Foot soak, nail trim, cuticle care and polish", 30.00, 60),
            ("Spa Pedicure", "Luxury treatment with exfoliation and foot massage", 40.00, 75),
            ("Gel Pedicure", "Long-lasting gel polish pedicure", 38.00, 70),
            ("Medical Pedicure", "Therapeutic treatment for problem feet", 50.00, 90),
            ("Express Pedicure", "Quick toenail trim and polish", 25.00, 45),
            
            # Nail Art & Extensions
            ("Nail Art (Simple)", "Basic designs and patterns per nail", 5.00, 15),
            ("Nail Art (Complex)", "Detailed artwork and 3D designs per nail", 10.00, 30),
            ("Acrylic Nails (Full Set)", "Complete set of acrylic extensions", 55.00, 120),
            ("Acrylic Nails (Refill)", "Maintenance for existing acrylic nails", 35.00, 75),
            ("Gel Extensions", "Natural-looking gel nail extensions", 60.00, 120),
            ("Nail Repair", "Fix broken or damaged nails", 8.00, 15),
            ("Nail Strengthening Treatment", "Protein treatment to strengthen weak nails", 25.00, 30),
            ("Chrome Nails", "Mirror finish chrome powder application", 45.00, 90),
            ("Ombre/Gradient Nails", "Beautiful color transition designs", 40.00, 75),
            ("Rhinestone Application", "Decorative crystals and gems", 15.00, 30),
            
            # Removal Services
            ("Gel Removal", "Safe removal of gel polish", 15.00, 30),
            ("Acrylic Removal", "Professional removal of acrylic nails", 20.00, 45),
        ]
        
        # Lash Services  
        lash_services = [
            ("Classic Lash Extensions", "Individual lashes for natural enhancement", 80.00, 120),
            ("Volume Lash Extensions", "Multiple thin lashes per natural lash", 100.00, 150),
            ("Hybrid Lash Extensions", "Mix of classic and volume techniques", 90.00, 135),
            ("Mega Volume Lashes", "Ultra-dramatic volume with multiple ultra-fine lashes", 120.00, 180),
            ("Lash Lift", "Natural lash curl enhancement", 45.00, 60),
            ("Lash Tint", "Darken natural lashes with semi-permanent dye", 25.00, 30),
            ("Lash Lift + Tint", "Combined curl and tint treatment", 60.00, 75),
            ("Lash Extension Refill (2 weeks)", "Maintenance for existing extensions", 45.00, 60),
            ("Lash Extension Refill (3 weeks)", "Maintenance for existing extensions", 55.00, 75),
            ("Lash Extension Removal", "Safe removal of extensions", 25.00, 30),
            ("Lower Lash Extensions", "Extensions for bottom lashes", 30.00, 45),
            ("Colored Lash Extensions", "Extensions in various colors", 110.00, 150),
        ]
        
        # Eyebrow Services
        eyebrow_services = [
            ("Eyebrow Shaping", "Professional eyebrow shaping with tweezers", 20.00, 30),
            ("Eyebrow Waxing", "Hair removal with wax for clean shape", 18.00, 20),
            ("Eyebrow Threading", "Precise hair removal with thread", 22.00, 25),
            ("Eyebrow Tinting", "Semi-permanent color for fuller look", 25.00, 30),
            ("Eyebrow Lamination", "Brow styling treatment for fuller appearance", 35.00, 45),
            ("Henna Brows", "Natural dye for longer-lasting color", 30.00, 45),
            ("Microblading", "Semi-permanent tattoo technique for natural brows", 250.00, 180),
        ]
        
        # Create services
        for name, description, price, duration in nail_services:
            Service.objects.get_or_create(
                name=name,
                category=nail_category,
                defaults={
                    'description': description,
                    'price': price,
                    'duration_minutes': duration,
                    'is_active': True
                }
            )
        
        for name, description, price, duration in lash_services:
            Service.objects.get_or_create(
                name=name,
                category=lash_category,
                defaults={
                    'description': description,
                    'price': price,
                    'duration_minutes': duration,
                    'is_active': True
                }
            )
            
        for name, description, price, duration in eyebrow_services:
            Service.objects.get_or_create(
                name=name,
                category=eyebrow_category,
                defaults={
                    'description': description,
                    'price': price,
                    'duration_minutes': duration,
                    'is_active': True
                }
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(nail_services + lash_services + eyebrow_services)} services!'
            )
        )
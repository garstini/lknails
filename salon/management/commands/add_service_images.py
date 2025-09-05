from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from salon.models import Service
import requests
from io import BytesIO

class Command(BaseCommand):
    help = 'Add demo images to services'

    def handle(self, *args, **options):
        # Beautiful nail and lash demo images
        service_images = {
            # Nails Services
            'Classic Manicure': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=400&fit=crop',
            'French Manicure': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&h=400&fit=crop',
            'Gel Manicure': 'https://images.unsplash.com/photo-1560457079-9a6532ccb118?w=400&h=400&fit=crop',
            'Express Manicure': 'https://images.unsplash.com/photo-1610992015732-2449b76344bc?w=400&h=400&fit=crop',
            'Luxury Spa Manicure': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=400&fit=crop',
            'Classic Pedicure': 'https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?w=400&h=400&fit=crop',
            'Spa Pedicure': 'https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=400&h=400&fit=crop',
            'Gel Pedicure': 'https://images.unsplash.com/photo-1560457079-9a6532ccb118?w=400&h=400&fit=crop',
            'Medical Pedicure': 'https://images.unsplash.com/photo-1487296744692-5514d8983738?w=400&h=400&fit=crop',
            'Express Pedicure': 'https://images.unsplash.com/photo-1567721913486-6585f069b332?w=400&h=400&fit=crop',
            'Nail Art (Simple)': 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=400&h=400&fit=crop',
            'Nail Art (Complex)': 'https://images.unsplash.com/photo-1643073875337-b1b8e2b1daf5?w=400&h=400&fit=crop',
            'Acrylic Nails (Full Set)': 'https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?w=400&h=400&fit=crop',
            'Acrylic Nails (Refill)': 'https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?w=400&h=400&fit=crop',
            'Gel Extensions': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=400&fit=crop',
            'Nail Repair': 'https://images.unsplash.com/photo-1625699493798-c4abf1688d32?w=400&h=400&fit=crop',
            'Nail Strengthening Treatment': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',
            'Chrome Nails': 'https://images.unsplash.com/photo-1643073875337-b1b8e2b1daf5?w=400&h=400&fit=crop',
            'Ombre/Gradient Nails': 'https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=400&h=400&fit=crop',
            'Rhinestone Application': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=400&fit=crop',
            'Gel Removal': 'https://images.unsplash.com/photo-1567721913486-6585f069b332?w=400&h=400&fit=crop',
            'Acrylic Removal': 'https://images.unsplash.com/photo-1567721913486-6585f069b332?w=400&h=400&fit=crop',

            # Lash Services
            'Classic Lash Extensions': 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=400&fit=crop',
            'Volume Lash Extensions': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=400&h=400&fit=crop',
            'Hybrid Lash Extensions': 'https://images.unsplash.com/photo-1585652757141-bf4a4aa786c0?w=400&h=400&fit=crop',
            'Mega Volume Lashes': 'https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=400&h=400&fit=crop',
            'Lash Lift': 'https://images.unsplash.com/photo-1581342748008-aac7a5a6712a?w=400&h=400&fit=crop',
            'Lash Tint': 'https://images.unsplash.com/photo-1542068829-1115f0b7c4ae?w=400&h=400&fit=crop',
            'Lash Lift + Tint': 'https://images.unsplash.com/photo-1581342748008-aac7a5a6712a?w=400&h=400&fit=crop',
            'Lash Extension Refill (2 weeks)': 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=400&fit=crop',
            'Lash Extension Refill (3 weeks)': 'https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=400&h=400&fit=crop',
            'Lash Extension Removal': 'https://images.unsplash.com/photo-1585652757141-bf4a4aa786c0?w=400&h=400&fit=crop',
            'Lower Lash Extensions': 'https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=400&h=400&fit=crop',
            'Colored Lash Extensions': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=400&h=400&fit=crop',

            # Eyebrow Services
            'Eyebrow Shaping': 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=400&h=400&fit=crop',
            'Eyebrow Waxing': 'https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400&h=400&fit=crop',
            'Eyebrow Threading': 'https://images.unsplash.com/photo-1581342748008-aac7a5a6712a?w=400&h=400&fit=crop',
            'Eyebrow Tinting': 'https://images.unsplash.com/photo-1542068829-1115f0b7c4ae?w=400&h=400&fit=crop',
            'Eyebrow Lamination': 'https://images.unsplash.com/photo-1585652757141-bf4a4aa786c0?w=400&h=400&fit=crop',
            'Henna Brows': 'https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=400&h=400&fit=crop',
            'Microblading': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=400&h=400&fit=crop',
        }

        # Add images to services
        services = Service.objects.all()
        for service in services:
            if service.name in service_images and not service.image:
                try:
                    image_url = service_images[service.name]
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        image_content = ContentFile(response.content)
                        service.image.save(
                            f"{service.name.lower().replace(' ', '_')}.jpg",
                            image_content,
                            save=True
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'Added image for {service.name}')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to add image for {service.name}: {e}')
                    )
        
        self.stdout.write(self.style.SUCCESS('Successfully added demo images to services!'))
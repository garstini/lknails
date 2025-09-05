from django.core.management.base import BaseCommand
from salon.models import Service
from django.core.files import File
from django.conf import settings
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io


class Command(BaseCommand):
    help = 'Assign appropriate images to services'

    def create_placeholder_image(self, text, color, filename):
        """Create a placeholder image with text and color"""
        width, height = 400, 300
        image = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(image)
        
        # Try to use a font, fall back to default if not available
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Calculate text size and position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with outline for better visibility
        draw.text((x-1, y-1), text, fill='black', font=font)
        draw.text((x+1, y-1), text, fill='black', font=font)
        draw.text((x-1, y+1), text, fill='black', font=font)
        draw.text((x+1, y+1), text, fill='black', font=font)
        draw.text((x, y), text, fill='white', font=font)
        
        # Save to media/services/
        services_dir = os.path.join(settings.MEDIA_ROOT, 'services')
        os.makedirs(services_dir, exist_ok=True)
        
        image_path = os.path.join(services_dir, filename)
        image.save(image_path, 'JPEG')
        return f'services/{filename}'

    def handle(self, *args, **options):
        # Service image mappings
        service_images = {
            # Nail services - existing images
            'Maniküre ab': 'services/classic_manicure.jpg',
            'Mit Shellac': 'services/gel_manicure.jpg',
            'Pediküre mit Massage': 'services/spa_pedicure.jpg',
            'Pediküre mit Shellac inkl. Massage': 'services/gel_pedicure.jpg',
            'Pediküre mit Acryl inkl. Massage': 'services/classic_pedicure.jpg',
            'NEUMODELLAGE: Natur': 'services/gel_manicure.jpg',
            'NEUMODELLAGE: mit Farbe': 'services/french_manicure.jpg',
            'NEUMODELLAGE: Weiß / Babyboomer / Ombre / French / Glitzer': 'services/french_manicure.jpg',
            'NEUMODELLAGE: Trend mit Farbe Babyboomer / Ombre / French / Glitzer': 'services/luxury_spa_manicure.jpg',
            'NEUMODELLAGE: Zehenmodellage oder Neu': 'services/gel_pedicure.jpg',
            'AUFFÜLLEN: Natur': 'services/gel_manicure.jpg',
            'AUFFÜLLEN: mit Farbe': 'services/french_manicure.jpg',
            'AUFFÜLLEN: Weiß Babyboomer / Ombre / French / Glitzer': 'services/luxury_spa_manicure.jpg',
            'AUFFÜLLEN: Trend mit Farbe Babyboomer / Ombre / French / Glitzer': 'services/luxury_spa_manicure.jpg',
        }

        # Create placeholder images for eyelash services
        eyelash_images = {}
        eyelash_colors = {
            'Classic 1:1': '#FF69B4',  # Hot pink
            'Light Volume 2D-3D': '#FF1493',  # Deep pink
            'Volume 4D-5D': '#DC143C',  # Crimson
            'Mega Volume ab 6D': '#8B0000',  # Dark red
            'Sonstiges': '#9370DB',  # Medium purple
        }

        # Create placeholder images for eyelash subcategories
        for subcategory, color in eyelash_colors.items():
            safe_name = subcategory.replace(' ', '_').replace(':', '').replace('-', '_').lower()
            filename = f'eyelash_{safe_name}.jpg'
            image_path = self.create_placeholder_image(
                subcategory.replace(' ', '\\n'), 
                color, 
                filename
            )
            
            # Assign to all services in this subcategory
            services_in_subcategory = Service.objects.filter(subcategory=subcategory)
            for service in services_in_subcategory:
                eyelash_images[service.name] = image_path

        # Create default images for design services
        self.create_placeholder_image('Nail Design', '#FFD700', 'nail_design.jpg')
        service_images['Überlänge'] = 'services/nail_design.jpg'
        service_images['Strass-Stein'] = 'services/nail_design.jpg'

        # Combine all image mappings
        all_images = {**service_images, **eyelash_images}

        # Assign images to services
        updated_count = 0
        for service in Service.objects.all():
            if service.name in all_images:
                image_path = all_images[service.name]
                if not service.image or service.image.name != image_path:
                    service.image = image_path
                    service.save()
                    updated_count += 1
                    self.stdout.write(f'✓ Updated {service.name} with image: {image_path}')
            else:
                # Use category-based default
                if service.category.name == 'Nägel':
                    service.image = 'services/classic_manicure.jpg'
                    service.save()
                    updated_count += 1
                    self.stdout.write(f'✓ Default nail image for {service.name}')
                elif service.category.name == 'Wimpern':
                    if service.subcategory:
                        safe_name = service.subcategory.replace(' ', '_').replace(':', '').replace('-', '_').lower()
                        service.image = f'services/eyelash_{safe_name}.jpg'
                    else:
                        service.image = 'services/eyelash_classic_11.jpg'
                    service.save()
                    updated_count += 1
                    self.stdout.write(f'✓ Default eyelash image for {service.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} services with images')
        )
        
        # Show statistics
        total_services = Service.objects.count()
        services_with_images = Service.objects.exclude(image='').count()
        
        self.stdout.write(f'\\nStatistics:')
        self.stdout.write(f'Total services: {total_services}')
        self.stdout.write(f'Services with images: {services_with_images}')
        self.stdout.write(f'Services without images: {total_services - services_with_images}')
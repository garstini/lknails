from django.core.management.base import BaseCommand
from salon.models import Service


class Command(BaseCommand):
    help = 'Fix eyelash service image assignments'

    def handle(self, *args, **options):
        # Subcategory to image mapping
        subcategory_images = {
            'Classic 1:1': 'services/eyelash_classic_11.jpg',
            'Light Volume 2D-3D': 'services/eyelash_light_volume_2d_3d.jpg',
            'Volume 4D-5D': 'services/eyelash_volume_4d_5d.jpg',
            'Mega Volume ab 6D': 'services/eyelash_mega_volume_ab_6d.jpg',
            'Sonstiges': 'services/eyelash_sonstiges.jpg',
        }

        updated_count = 0
        for service in Service.objects.filter(category__name='Wimpern'):
            if service.subcategory in subcategory_images:
                new_image = subcategory_images[service.subcategory]
                if service.image != new_image:
                    service.image = new_image
                    service.save()
                    updated_count += 1
                    self.stdout.write(
                        f'✓ Updated {service.subcategory} - {service.name} with {new_image}'
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} eyelash services')
        )

        # Show current assignments
        self.stdout.write(f'\\nCurrent assignments:')
        for subcategory in subcategory_images.keys():
            count = Service.objects.filter(subcategory=subcategory).count()
            image = subcategory_images[subcategory]
            self.stdout.write(f'{subcategory}: {count} services → {image}')
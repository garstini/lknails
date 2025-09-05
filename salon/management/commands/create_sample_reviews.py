from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from salon.models import Review, Service, Customer, Staff
import random


class Command(BaseCommand):
    help = 'Create sample reviews for demonstration'

    def handle(self, *args, **options):
        # Sample review data in German
        reviews_data = [
            {
                'rating': 5,
                'comment': 'Absolut perfekt! Das beste Nagelstudio in der Stadt. Die Mitarbeiterinnen sind super professionell und freundlich. Meine Nägel sehen fantastisch aus!',
            },
            {
                'rating': 5,
                'comment': 'Bin total begeistert von der Qualität der Arbeit! Die Wimpernverlängerung ist wunderschön geworden. Kann ich nur weiterempfehlen!',
            },
            {
                'rating': 4,
                'comment': 'Sehr schöne Behandlung, tolles Ambiente und faire Preise. Kleine Wartezeit, aber das war es absolut wert. Komme definitiv wieder!',
            },
            {
                'rating': 5,
                'comment': 'Wow! So professionell und sauber. Die French Maniküre ist perfekt geworden. Das Personal ist sehr aufmerksam und kompetent.',
            },
            {
                'rating': 5,
                'comment': 'Meine Gelnägel halten jetzt schon 3 Wochen ohne Probleme! Bin super zufrieden mit der Beratung und dem Ergebnis. Top Service!',
            },
            {
                'rating': 4,
                'comment': 'Tolles Studio mit modernster Ausstattung. Die Pediküre war sehr entspannend und gründlich. Preise sind angemessen für die Qualität.',
            },
            {
                'rating': 5,
                'comment': 'Endlich ein Studio, das auf Hygiene und Qualität achtet! Meine Wimpern sehen so natürlich und schön aus. Vielen Dank!',
            },
            {
                'rating': 4,
                'comment': 'Sehr freundlicher Service und schöne Ergebnisse. Das Nageldesign ist genau so geworden wie ich es mir vorgestellt habe.',
            },
            {
                'rating': 5,
                'comment': 'Beste Erfahrung ever! Die Mitarbeiterin hat sich so viel Zeit genommen und perfekt beraten. Fühle mich wie eine Prinzessin!',
            },
            {
                'rating': 4,
                'comment': 'Saubere Arbeit, schönes Ambiente und nettes Personal. Die Shellac Behandlung hält wirklich lange. Komme gerne wieder!',
            }
        ]

        # Get or create sample customers
        sample_customers = []
        customer_names = [
            ('Anna', 'Mueller'), ('Lisa', 'Schmidt'), ('Maria', 'Weber'),
            ('Sarah', 'Bauer'), ('Julia', 'Fischer'), ('Nicole', 'Wagner'),
            ('Petra', 'Becker'), ('Stefanie', 'Schulz'), ('Claudia', 'Hoffmann'),
            ('Andrea', 'Schaefer')
        ]

        for first_name, last_name in customer_names:
            username = f"{first_name.lower()}.{last_name.lower()}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f"{username}@example.com"
                }
            )
            customer, created = Customer.objects.get_or_create(user=user)
            sample_customers.append(customer)

        # Get some services and staff
        services = list(Service.objects.filter(is_active=True))
        staff_members = list(Staff.objects.all())

        if not services:
            self.stdout.write(
                self.style.WARNING('No services found. Please create some services first.')
            )
            return

        if not staff_members:
            self.stdout.write(
                self.style.WARNING('No staff members found. Please create some staff first.')
            )
            return

        # Create reviews
        created_count = 0
        for i, review_data in enumerate(reviews_data):
            if i < len(sample_customers):
                customer = sample_customers[i]
                service = random.choice(services)
                staff = random.choice(staff_members)

                # Check if review already exists for this customer and service
                if not Review.objects.filter(customer=customer, service=service).exists():
                    Review.objects.create(
                        customer=customer,
                        service=service,
                        staff=staff,
                        rating=review_data['rating'],
                        comment=review_data['comment'],
                        is_approved=True,
                        is_featured=review_data['rating'] == 5 and created_count < 3  # Mark first 3 5-star reviews as featured
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created review by {customer.user.first_name} for {service.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample reviews!')
        )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\nYou can now:\n'
                    '- View reviews at /reviews/\n'
                    '- Manage reviews in the admin panel\n'
                    '- See review buttons on completed appointments'
                )
            )
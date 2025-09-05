from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Setup social authentication apps for Google and Facebook'

    def handle(self, *args, **options):
        # Ensure we have a site
        site, created = Site.objects.get_or_create(
            domain='127.0.0.1:8000',
            defaults={'name': 'LK Nails & Lashes Local'}
        )
        
        # Create Google OAuth app (with placeholder keys for development)
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': 'your-google-client-id-here.apps.googleusercontent.com',
                'secret': 'your-google-client-secret-here',
            }
        )
        google_app.sites.add(site)
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Google OAuth app'))
        else:
            self.stdout.write(self.style.SUCCESS('Google OAuth app already exists'))
        
        # Create Facebook OAuth app (with placeholder keys for development)
        facebook_app, created = SocialApp.objects.get_or_create(
            provider='facebook',
            defaults={
                'name': 'Facebook OAuth',
                'client_id': 'your-facebook-app-id-here',
                'secret': 'your-facebook-app-secret-here',
            }
        )
        facebook_app.sites.add(site)
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Facebook OAuth app'))
        else:
            self.stdout.write(self.style.SUCCESS('Facebook OAuth app already exists'))
        
        self.stdout.write(
            self.style.WARNING(
                '\nIMPORTANT: To enable social login, you need to:'
                '\n1. Go to Google Cloud Console (https://console.cloud.google.com/)'
                '\n2. Create a new project or select existing project'
                '\n3. Enable Google+ API'
                '\n4. Create OAuth 2.0 credentials'
                '\n5. Set authorized redirect URI: http://127.0.0.1:8000/accounts/google/login/callback/'
                '\n6. Update the Google app in Django admin with real client ID and secret'
                '\n'
                '\nFor Facebook:'
                '\n1. Go to Facebook Developers (https://developers.facebook.com/)'
                '\n2. Create a new app'
                '\n3. Add Facebook Login product'
                '\n4. Set Valid OAuth Redirect URIs: http://127.0.0.1:8000/accounts/facebook/login/callback/'
                '\n5. Update the Facebook app in Django admin with real app ID and secret'
            )
        )
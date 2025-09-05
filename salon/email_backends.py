from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.conf import settings
from .models import EmailConfiguration


class DynamicEmailBackend(SMTPEmailBackend):
    """
    Custom email backend that uses EmailConfiguration from database
    """
    
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        
        # Try to get email configuration from database
        try:
            email_config = EmailConfiguration.objects.filter(is_active=True).first()
            
            if email_config:
                # Use database configuration
                host = email_config.smtp_server
                port = email_config.smtp_port
                username = email_config.smtp_username
                password = email_config.smtp_password
                use_tls = email_config.use_tls
                use_ssl = False
                
                # Set default from email
                if not hasattr(settings, 'DEFAULT_FROM_EMAIL'):
                    settings.DEFAULT_FROM_EMAIL = email_config.from_email
                    
        except Exception as e:
            # Fallback to default settings if database is not available
            print(f"Could not load email configuration from database: {e}")
            # Use Django default settings
            pass
        
        super().__init__(
            host=host, port=port, username=username, password=password,
            use_tls=use_tls, fail_silently=fail_silently, use_ssl=use_ssl,
            timeout=timeout, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile,
            **kwargs
        )
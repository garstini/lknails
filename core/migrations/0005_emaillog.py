from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_alter_sitesettings_smtp_host_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(max_length=200)),
                ("recipient_list", models.TextField(help_text="Comma-separated recipient emails")),
                ("from_email", models.CharField(blank=True, max_length=255)),
                ("body", models.TextField(blank=True)),
                ("template_type", models.CharField(blank=True, max_length=32)),
                ("status", models.CharField(choices=[("sent", "Sent"), ("failed", "Failed")], max_length=16)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]

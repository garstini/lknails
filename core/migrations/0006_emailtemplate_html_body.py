from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_emaillog"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailtemplate",
            name="html_body",
            field=models.TextField(
                blank=True,
                help_text="Optional HTML version of the email. Supports the same placeholders as body.",
            ),
        ),
    ]

# Generated by Django 5.1.1 on 2024-12-08 12:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0011_remove_userprofile_email_userprofile_is_verified_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productpurchase',
            name='delivery_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 8, 14, 17, 55, 328613, tzinfo=datetime.timezone.utc)),
        ),
    ]
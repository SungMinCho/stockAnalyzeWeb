# Generated by Django 2.0 on 2018-01-11 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20180111_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulation',
            name='progress',
            field=models.FloatField(default=0.0),
        ),
    ]

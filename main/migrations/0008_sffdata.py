# Generated by Django 2.0 on 2018-01-15 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_simulation_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='SffData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.CharField(max_length=20)),
                ('y', models.FloatField(default=0.0)),
                ('y2', models.FloatField(default=0.0)),
                ('chart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Chart')),
            ],
        ),
    ]
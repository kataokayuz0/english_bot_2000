# Generated by Django 3.2 on 2023-05-23 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
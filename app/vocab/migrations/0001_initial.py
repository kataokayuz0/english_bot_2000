# Generated by Django 3.2 on 2023-05-28 08:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wordbook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=50, verbose_name='単語')),
                ('meaning', models.TextField(blank=True, verbose_name='意味')),
                ('pronunciation', models.CharField(blank=True, max_length=50, null=True, verbose_name='発音')),
                ('category', models.CharField(blank=True, max_length=50, null=True, verbose_name='品詞')),
                ('context', models.TextField(blank=True, null=True, verbose_name='文脈')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザーID')),
            ],
            options={
                'verbose_name': '単語帳',
                'verbose_name_plural': '単語帳',
                'db_table': 'wordbook',
                'ordering': ['word'],
            },
        ),
        migrations.AddConstraint(
            model_name='wordbook',
            constraint=models.UniqueConstraint(fields=('user_id', 'word'), name='unique_user_word'),
        ),
    ]

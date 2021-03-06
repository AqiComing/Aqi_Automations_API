# Generated by Django 2.0.5 on 2020-08-05 12:00

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
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, default='N/A', max_length=11, verbose_name='phone number')),
                ('openId', models.CharField(default=0, max_length=50, verbose_name='唯一标识')),
                ('unionId', models.CharField(default=0, max_length=50, verbose_name='企业唯一标识')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
    ]

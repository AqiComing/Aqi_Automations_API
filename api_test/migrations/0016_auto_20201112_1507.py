# Generated by Django 2.0.5 on 2020-11-12 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_test', '0015_auto_20201026_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmember',
            name='permission_type',
            field=models.CharField(choices=[('超级管理员', '超级管理员'), ('开发人员', '开发人员'), ('测试人员', '测试人员')], max_length=50, verbose_name='权限角色'),
        ),
    ]

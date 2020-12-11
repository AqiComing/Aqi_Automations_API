# Generated by Django 2.0.5 on 2020-10-26 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_test', '0014_automationcaseapi_automationhead_automationparameter_automationparameterraw_automationresponsejson_a'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmember',
            name='permission_type',
            field=models.CharField(choices=[('开发人员', '开发人员'), ('超级管理员', '超级管理员'), ('测试人员', '测试人员')], max_length=50, verbose_name='权限角色'),
        ),
    ]
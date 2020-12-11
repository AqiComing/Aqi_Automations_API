# Generated by Django 2.0.5 on 2020-08-21 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_test', '0009_projectmember'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='接口一级分组')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_test.Project', verbose_name='项目')),
            ],
            options={
                'verbose_name': '接口一级分组',
                'verbose_name_plural': '接口一级分组',
            },
        ),
        migrations.AlterField(
            model_name='projectmember',
            name='permission_type',
            field=models.CharField(choices=[('测试人员', '测试人员'), ('超级管理员', '超级管理员'), ('开发人员', '开发人员')], max_length=50, verbose_name='权限角色'),
        ),
    ]
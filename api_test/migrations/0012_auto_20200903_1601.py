# Generated by Django 2.0.5 on 2020-09-03 08:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_test', '0011_auto_20200824_1700'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestCaseGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='测试用例分组')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_test.Project', verbose_name='项目')),
            ],
            options={
                'verbose_name': '测试用例分组',
                'verbose_name_plural': '测试用例分组管理',
            },
        ),
        migrations.AlterField(
            model_name='apiinfo',
            name='mock_code',
            field=models.CharField(blank=True, choices=[('0', '0'), ('200', '200'), ('302', '302'), ('400', '400'), ('404', '404'), ('500', '500'), ('502', '502')], max_length=50, null=True, verbose_name='Http状态'),
        ),
        migrations.AlterField(
            model_name='projectmember',
            name='permission_type',
            field=models.CharField(choices=[('开发人员', '开发人员'), ('测试人员', '测试人员'), ('超级管理员', '超级管理员')], max_length=50, verbose_name='权限角色'),
        ),
    ]
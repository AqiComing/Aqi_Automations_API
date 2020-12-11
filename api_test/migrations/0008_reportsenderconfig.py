# Generated by Django 2.0.5 on 2020-08-20 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_test', '0007_auto_20200818_1031'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportSenderConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sender_mailbox', models.EmailField(blank=True, max_length=1024, null=True, verbose_name='发件人邮箱')),
                ('user_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='用户名')),
                ('mail_token', models.CharField(blank=True, max_length=1024, null=True, verbose_name='邮箱口令')),
                ('mail_smtp', models.CharField(blank=True, max_length=1024, null=True, verbose_name='邮箱服务器')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_test.Project', verbose_name='项目')),
            ],
            options={
                'verbose_name': '邮件发送配置',
                'verbose_name_plural': '邮件发送配置',
            },
        ),
    ]
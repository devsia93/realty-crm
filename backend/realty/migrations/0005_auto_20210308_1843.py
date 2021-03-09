# Generated by Django 3.1.7 on 2021-03-08 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0004_task_deal'),
        ('realty', '0004_client_worker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deal',
            name='worker',
        ),
        migrations.AddField(
            model_name='deal',
            name='main_worker',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deals', to='company.worker', verbose_name='Сотрудник #1'),
        ),
        migrations.AddField(
            model_name='deal',
            name='realty',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deals', to='realty.realty', verbose_name='Недвижимость'),
        ),
        migrations.AddField(
            model_name='deal',
            name='sub_worker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sub_deals', to='company.worker', verbose_name='Сотрудник #2'),
        ),
    ]
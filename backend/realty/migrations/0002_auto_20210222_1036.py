# Generated by Django 3.1.7 on 2021-02-22 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тип договора',
                'verbose_name_plural': 'Типы договоров',
            },
        ),
        migrations.AddField(
            model_name='realty',
            name='contract',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='realties', to='realty.contract', verbose_name='Тип договора'),
        ),
    ]

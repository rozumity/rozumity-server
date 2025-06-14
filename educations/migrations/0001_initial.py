# Generated by Django 5.2.1 on 2025-06-14 14:10

import django.core.validators
import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Speciality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='053', max_length=3, validators=[django.core.validators.MinLengthValidator(3)])),
                ('title', models.CharField(default='Psychology', max_length=128)),
                ('code_world', models.CharField(default='0313', max_length=4, validators=[django.core.validators.MinLengthValidator(4)])),
                ('title_world', models.CharField(default='Psychology', max_length=128)),
                ('is_medical', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Speciality',
                'verbose_name_plural': 'Specialities',
            },
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=128)),
                ('title_world', models.CharField(default='', max_length=128)),
                ('country', django_countries.fields.CountryField(max_length=2)),
            ],
            options={
                'verbose_name': 'University',
                'verbose_name_plural': 'Universities',
            },
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degree', models.SmallIntegerField(choices=[(0, 'Course'), (1, 'Undergraduate'), (2, 'Specialist'), (3, 'Master'), (4, 'Postgraduate'), (5, 'Doctor')], default=0)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('speciality', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='educations.speciality')),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='educations.university')),
            ],
            options={
                'verbose_name': 'Education',
                'verbose_name_plural': 'Educations',
            },
        ),
    ]

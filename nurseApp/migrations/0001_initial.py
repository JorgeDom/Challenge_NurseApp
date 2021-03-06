# Generated by Django 2.1 on 2020-05-14 04:01

from django.db import migrations, models
import djongo.models.fields
import nurseApp.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name and last name of the patient.', max_length=100, verbose_name='Name and Last name')),
                ('age', models.PositiveSmallIntegerField(help_text='Specify how old is the patient.', max_length=3, verbose_name='Age')),
                ('custom_id', models.PositiveSmallIntegerField(help_text='Add some Personal ID of the patient. (e.g. ID Card number or Passport number)', max_length=10, verbose_name='Patient ID')),
                ('records', djongo.models.fields.EmbeddedModelField(default={}, model_container=nurseApp.models.Record, null=True, verbose_name='Records')),
            ],
        ),
    ]

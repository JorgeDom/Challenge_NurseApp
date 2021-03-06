# Generated by Django 2.1 on 2020-05-14 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nurseApp', '0005_auto_20200514_0910'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='status',
            field=models.CharField(default='active', max_length=10),
        ),
        migrations.AlterField(
            model_name='patient',
            name='custom_id',
            field=models.PositiveIntegerField(help_text='Later he/she will use it to see his/her historical data (e.g. ID Card number or Passport number)', unique=True, verbose_name='ID'),
        ),
    ]

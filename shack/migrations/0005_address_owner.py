# Generated by Django 2.1.7 on 2019-04-09 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shack', '0004_auto_20180523_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='owner',
            field=models.TextField(blank=True, null=True),
        ),
    ]

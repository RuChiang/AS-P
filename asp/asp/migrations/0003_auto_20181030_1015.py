# Generated by Django 2.1.2 on 2018-10-30 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asp', '0002_auto_20181030_0948'),
    ]

    operations = [
        migrations.RenameField(
            model_name='distance',
            old_name='from_host',
            new_name='host_a',
        ),
        migrations.RenameField(
            model_name='distance',
            old_name='to_host',
            new_name='host_b',
        ),
    ]

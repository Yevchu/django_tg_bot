# Generated by Django 5.1.6 on 2025-03-11 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0002_remove_group_max_member_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledmessage',
            name='image',
            field=models.BinaryField(blank=True),
        ),
    ]

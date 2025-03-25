# Generated by Django 5.1.6 on 2025-03-22 12:11

import core.storages
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('image', models.ImageField(storage=core.storages.ProductStorage(), upload_to='')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'product_image',
                'verbose_name_plural': 'product_images',
                'db_table': 'product_images',
            },
        ),
        migrations.CreateModel(
            name='ProfileImage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('image', models.ImageField(storage=core.storages.ProfileStorage(), upload_to='')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'profile_image',
                'verbose_name_plural': 'profile_images',
                'db_table': 'profile_images',
            },
        ),
    ]


from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='offers/')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('delivery_time_in_days', models.IntegerField(help_text='Estimated delivery time in days')),
                ('revisions', models.IntegerField(default=0, help_text='Number of revisions included')),
                ('features', models.JSONField(blank=True, default=list)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'offers',
                'ordering': ['-created_at'],
            },
        ),
    ]

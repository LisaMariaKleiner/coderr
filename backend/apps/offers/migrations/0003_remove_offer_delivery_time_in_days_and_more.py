
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='delivery_time_in_days',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='features',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='price',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='revisions',
        ),
        migrations.CreateModel(
            name='OfferDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('revisions', models.IntegerField(default=0)),
                ('delivery_time_in_days', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('features', models.JSONField(blank=True, default=list)),
                ('offer_type', models.CharField(choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')], max_length=20)),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='offers.offer')),
            ],
            options={
                'db_table': 'offer_details',
                'ordering': ['offer', 'price'],
            },
        ),
    ]

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('companies', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='CustomerAccount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('external_id', models.CharField(blank=True, default='', max_length=128)),
                ('name', models.CharField(max_length=255)),
                ('segment', models.CharField(choices=[('enterprise', 'Enterprise'), ('wholesale', 'Wholesale'), ('smb', 'SMB'), ('residential', 'Residential')], db_index=True, default='enterprise', max_length=32)),
                ('status', models.CharField(choices=[('active', 'Active'), ('suspended', 'Suspended'), ('churned', 'Churned')], db_index=True, default='active', max_length=32)),
                ('contact_name', models.CharField(blank=True, default='', max_length=255)),
                ('contact_email', models.EmailField(blank=True, default='', max_length=254)),
                ('contact_phone', models.CharField(blank=True, default='', max_length=64)),
                ('service_address', models.TextField(blank=True, default='')),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operation_customers', to='companies.company')),
            ],
            options={'db_table': 'ops_customer_accounts'},
        ),
    ]


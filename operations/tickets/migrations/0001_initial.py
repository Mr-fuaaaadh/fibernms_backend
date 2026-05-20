import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('accounts', '0002_user_mfa_secret_authevent_usersession'),
        ('companies', '0001_initial'),
        ('customers', '0001_initial'),
        ('incidents', '0001_initial'),
        ('workforce', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ticket_number', models.CharField(db_index=True, max_length=32)),
                ('subject', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('priority', models.CharField(choices=[('p1', 'P1'), ('p2', 'P2'), ('p3', 'P3'), ('p4', 'P4')], db_index=True, default='p3', max_length=8)),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('waiting_customer', 'Waiting Customer'), ('escalated', 'Escalated'), ('resolved', 'Resolved'), ('closed', 'Closed')], db_index=True, default='open', max_length=32)),
                ('response_due_at', models.DateTimeField(blank=True, null=True)),
                ('resolution_due_at', models.DateTimeField(blank=True, null=True)),
                ('escalated_at', models.DateTimeField(blank=True, null=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets', to='workforce.engineerteam')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to='accounts.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='companies.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tickets', to='accounts.user')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets', to='customers.customeraccount')),
                ('incident', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets', to='incidents.incident')),
            ],
            options={'db_table': 'ops_tickets'},
        ),
        migrations.CreateModel(
            name='TicketComment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('body', models.TextField()),
                ('is_internal', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ticket_comments', to='accounts.user')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_comments', to='companies.company')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tickets.ticket')),
            ],
            options={'db_table': 'ops_ticket_comments'},
        ),
        migrations.CreateModel(
            name='TicketAttachment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='ticket_attachments/%Y/%m/%d/')),
                ('filename', models.CharField(max_length=255)),
                ('content_type', models.CharField(blank=True, default='', max_length=128)),
                ('size_bytes', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_attachments', to='companies.company')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='tickets.ticket')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ticket_attachments', to='accounts.user')),
            ],
            options={'db_table': 'ops_ticket_attachments'},
        ),
    ]


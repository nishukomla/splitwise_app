# Generated by Django 4.1.2 on 2022-10-27 15:06

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0003_contact_remove_group_members_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money_owed', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('person1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person1', to=settings.AUTH_USER_MODEL)),
                ('person2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=30)),
                ('no_transactions', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money_owed', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.group')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=500)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('person1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mperson1', to=settings.AUTH_USER_MODEL)),
                ('person2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mperson2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('image', models.ImageField(blank=True, default='default_face.png', upload_to='profile_image')),
                ('no_of_messages', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_transaction_id', models.IntegerField(default=0)),
                ('description', models.CharField(max_length=30)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tag', models.CharField(choices=[('mv', 'Movies'), ('fd', 'Food'), ('tr', 'Travel'), ('ee', 'Electronics'), ('md', 'Medical'), ('sp', 'Shopping'), ('sv', 'Services'), ('st', 'Settle'), ('ot', 'Others')], max_length=2)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='added_by', to=settings.AUTH_USER_MODEL)),
                ('borrower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrower', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.group')),
                ('lender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lender', to=settings.AUTH_USER_MODEL)),
                ('paid_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='paid_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Contact',
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(through='app.Membership', to=settings.AUTH_USER_MODEL),
        ),
    ]
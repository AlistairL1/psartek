# Generated by Django 5.1.7 on 2025-04-07 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0010_remove_gameevaluation_poll_rank_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gameevaluation',
            old_name='total_rank',
            new_name='total_score',
        ),
    ]

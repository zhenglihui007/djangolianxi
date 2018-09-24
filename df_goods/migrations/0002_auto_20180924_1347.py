# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('df_goods', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goodsinfo',
            old_name='gxontent',
            new_name='gcontent',
        ),
    ]

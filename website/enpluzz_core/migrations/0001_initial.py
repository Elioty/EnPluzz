# EnPluzz
# Copyright (C) 2025  Elioty <roadkiller.cl@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Generated by Django 5.1.4 on 2025-03-09 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enp_id', models.CharField(max_length=255, unique=True)),
                ('order', models.IntegerField(default=None, null=True)),
            ],
            options={
                'indexes': [models.Index(fields=['enp_id'], name='enpluzz_cor_enp_id_4192f0_idx')],
            },
        ),
        migrations.CreateModel(
            name='GameMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enp_id', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'indexes': [models.Index(fields=['enp_id'], name='enpluzz_cor_enp_id_d02f66_idx')],
            },
        ),
        migrations.CreateModel(
            name='Rarity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enp_id', models.IntegerField(unique=True)),
                ('order', models.IntegerField(default=None, null=True)),
            ],
            options={
                'indexes': [models.Index(fields=['enp_id'], name='enpluzz_cor_enp_id_d78ed0_idx')],
            },
        ),
    ]

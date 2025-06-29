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

from django.db import models

class Element(models.Model):
    enp_id = models.CharField(max_length=255, unique=True)
    order  = models.IntegerField(default=None, null=True)

    class JsonMeta:
        is_enumerate = True
        default_elements = (
            {'enp_id': 'Purple', 'order':  0},
            {'enp_id': 'Yellow', 'order': 10},
            {'enp_id': 'Blue',   'order': 20},
            {'enp_id': 'Green',  'order': 30},
            {'enp_id': 'Red',    'order': 40},
            {'enp_id': 'All',    'order': 50},
        )

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class Rarity(models.Model):
    enp_id = models.IntegerField(unique=True)
    order  = models.IntegerField(default=None, null=True)

    class JsonMeta:
        is_enumerate = True
        default_elements = (
            {'enp_id': 1, 'order': 10},
            {'enp_id': 2, 'order': 20},
            {'enp_id': 3, 'order': 30},
            {'enp_id': 4, 'order': 40},
            {'enp_id': 5, 'order': 50},
        )

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

    def __int__(self) -> int:
        return self.enp_id

class GameMode(models.Model):
    enp_id = models.CharField(max_length=255, unique=True)

    class JsonMeta:
        is_enumerate = True
        default_elements = (
            {'enp_id': 'Classic'},
            {'enp_id':  'Dragon'},
        )

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

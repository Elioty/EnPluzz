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
from datetime import datetime

class BooleanFieldFromJson(models.BooleanField):
    def __init__(self, *args, json_field=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_field = json_field

class CharFieldFromJson(models.CharField):
    def __init__(self, *args, json_field=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_field = json_field

class IntegerFieldFromJson(models.IntegerField):
    def __init__(self, *args, json_field=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_field = json_field

class DateTimeFieldFromJson(models.DateTimeField):
    def __init__(self, *args, json_field=None, epoch_date=datetime.fromisoformat('2000-01-01 00:00:00+00:00'), **kwargs):
        super().__init__(*args, **kwargs)
        self.json_field = json_field
        self.epoch_date = epoch_date

class JSONFieldFromJson(models.JSONField):
    def __init__(self, *args, json_field=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_field = json_field

class ForeignKeyFromJson(models.ForeignKey):
    def __init__(self, *args, json_field=None, target_is_enumerate=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_field = json_field
        self.target_is_enumerate = target_is_enumerate

class ManyToManyFieldFromJson(models.ManyToManyField):
    def __init__(self, *args, json_field=None, target_is_enumerate=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_field = json_field
        self.target_is_enumerate = target_is_enumerate

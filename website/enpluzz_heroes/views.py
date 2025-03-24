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

from django.shortcuts import render, get_object_or_404
from datetime import datetime
from django.db.models import Q

from .models import Hero

def index(request):
    heroes = Hero.objects.select_related('family', 'special_skill', 'class_type', 'costume_bonus', 'parent_hero', 'parent_hero__costume_bonus').filter(is_default_rider=False).exclude(can_be_received_date__gt=datetime.now()).prefetch_related('costumes', 'parent_hero__costumes')
    return render(request, 'enpluzz_heroes/index.html', {'heroes': heroes })

def hero(request, hero_id):
    hero = get_object_or_404(Hero, Q(can_be_received_date__lte=datetime.now()) | Q(can_be_received_date=None), pk=hero_id, is_default_rider=False)
    return render(request, 'enpluzz_heroes/hero.html', {'hero': hero })

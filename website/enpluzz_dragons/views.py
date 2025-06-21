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

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from datetime import datetime, timezone
from django.db.models import Q, F, Count, Case, When

from enpluzz_core.models import Element, Rarity
from enpluzz_heroes.models import ClassType
from .models import *

def index(request, f_elements=[], f_rarities=[], f_class_types=[], f_mana_speeds=[], f_sort=[]):
    elements = Element.objects.values_list('enp_id', flat=True).order_by(F('order').asc(nulls_last=True))
    rarities = Rarity.objects.values_list('enp_id', flat=True).order_by('-enp_id')
    class_types = ClassType.objects.values_list('enp_id', flat=True).order_by('enp_id')
    mana_speeds = ManaSpeed.objects.annotate(nb_dragons=Count('dragons')).exclude(nb_dragons=0).values_list('enp_id', flat=True).order_by('max_mana')
    dragons = Dragon.objects.select_related('element', 'special_skill', 'dragon_spirit_class_bonuses', 'dragon_spirit_element_bonuses', 'mana_speed') \
                            .filter(Q(can_be_received_date__lte=datetime.now(timezone.utc)) | Q(can_be_received_date=None))

    # Filtering options
    if f_elements:
        f_elements = f_elements.split(',')
        if len([e for e in f_elements if e not in elements]):
            raise Http404("Invalid element filter")
        dragons = dragons.filter(element_id__in=f_elements)

    if f_rarities:
        try:
            f_rarities = [int(r) for r in f_rarities.split(',')]
        except:
            raise Http404("Invalid rarity filter")
        if len([r for r in f_rarities if r not in rarities]):
            raise Http404("Invalid rarity filter")
        dragons = dragons.filter(rarity_id__in=f_rarities)

    if f_class_types:
        f_class_types = f_class_types.split(',')
        if len([c for c in f_class_types if c not in class_types]):
            raise Http404("Invalid class filter")
        dragons = dragons.filter(dragon_spirit_class_bonuses_id__in=[c.lower() for c in f_class_types])

    if f_mana_speeds:
        f_mana_speeds = f_mana_speeds.split(',')
        if len([m for m in f_mana_speeds if m not in mana_speeds]):
            raise Http404("Invalid mana speed filter")
        dragons = dragons.filter(mana_speed_id__in=f_mana_speeds)

    # Sorting options
    order_by_args = []
    if f_sort:
        f_sort = set(f_sort.split(','))
        SORTING_OPTIONS = {
            'element':    lambda: F('element__order').asc(nulls_last=True),
            'rarity':     lambda: '-rarity_id',
            'class':      lambda: F('dragon_spirit_class_bonuses_id').asc(nulls_last=True),
            'mana_speed': lambda: 'mana_speed__max_mana',
        }
        if f_sort - SORTING_OPTIONS.keys():
            raise Http404("Invalid sorting options")
        for sorting_option in f_sort:
            order_by_args.append(SORTING_OPTIONS[sorting_option]())

    if not order_by_args: # Default sorting options
        order_by_args = [F('can_be_received_date').desc(nulls_last=True), F('origin_id'), F('rarity_id').desc()]
    dragons = dragons.order_by(*order_by_args)

    return render(request, 'enpluzz_dragons/index.html', {
        'elements': elements,
        'rarities': rarities,
        'class_types': class_types,
        'mana_speeds': mana_speeds,
        'f_elements': f_elements,
        'f_rarities': f_rarities,
        'f_class_types': f_class_types,
        'f_mana_speeds': f_mana_speeds,
        'f_sort': f_sort,
        'dragons': dragons,
    })

def query(request):
    if request.method != 'POST':
        return redirect('enpluzz_dragons:index')

    f_elements = []
    f_rarities = []
    f_class_types = []
    f_mana_speeds = []

    for (k, v) in request.POST.items():
        if v == 'on':
            if k.startswith('element_'):
                f_elements.append(k[len('element_'):])
            if k.startswith('rarity_'):
                f_rarities.append(k[len('rarity_'):])
            if k.startswith('class_type_'):
                f_class_types.append(k[len('class_type_'):])
            if k.startswith('mana_speed_'):
                f_mana_speeds.append(k[len('mana_speed_'):])

    kwargs = dict()
    if f_elements:
        kwargs['f_elements'] = ','.join(f_elements)
    if f_rarities:
        kwargs['f_rarities'] = ','.join(f_rarities)
    if f_class_types:
        kwargs['f_class_types'] = ','.join(f_class_types)
    if f_mana_speeds:
        kwargs['f_mana_speeds'] = ','.join(f_mana_speeds)
    return redirect('enpluzz_dragons:query', **kwargs)

def dragon(request, dragon_id):
    dragon = get_object_or_404(Dragon, Q(can_be_received_date__lte=datetime.now(timezone.utc)) | Q(can_be_received_date=None), pk=dragon_id)
    return render(request, 'enpluzz_dragons/dragon.html', {'dragon': dragon })

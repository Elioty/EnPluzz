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
from .models import *

def index(request, f_elements=[], f_rarities=[], f_families=[], f_class_types=[], f_emblems=[], f_mana_speeds=[], f_costume='', f_sort=[]):
    now_time = datetime.now(timezone.utc)
    elements = Element.objects.values_list('enp_id', flat=True).order_by(F('order').asc(nulls_last=True))
    rarities = Rarity.objects.values_list('enp_id', flat=True).order_by('-enp_id')
    families = Family.objects.exclude(heroes__is_default_rider=True, heroes__can_be_received_date__gt=now_time) \
                             .annotate(nb_heroes=Count('heroes')).exclude(nb_heroes=0).order_by(F('order').asc(nulls_last=True)) \
                             .annotate(fam_id=Case(
                                 When(family_set__isnull=False, then='family_set_id'),
                                 default='enp_id'
                             )).values_list('fam_id', flat=True).distinct()
    class_types = ClassType.objects.values_list('enp_id', flat=True).order_by('enp_id')
    mana_speeds = ManaSpeed.objects.annotate(nb_heroes=Count('heroes')).exclude(nb_heroes=0).values_list('enp_id', flat=True).order_by('max_mana')
    heroes = Hero.objects.select_related('element', 'family', 'special_skill', 'class_type', 'mana_speed', 'costume_bonus', 'parent_hero', 'parent_hero__costume_bonus') \
                         .exclude(is_default_rider=True, can_be_received_date__gt=now_time) \
                         .prefetch_related('costumes', 'parent_hero__costumes')

    # Filtering options
    if f_elements:
        f_elements = f_elements.split(',')
        if len([e for e in f_elements if e not in elements]):
            raise Http404("Invalid element filter")
        heroes = heroes.filter(element_id__in=f_elements)

    if f_rarities:
        try:
            f_rarities = [int(r) for r in f_rarities.split(',')]
        except:
            raise Http404("Invalid rarity filter")
        if len([r for r in f_rarities if r not in rarities]):
            raise Http404("Invalid rarity filter")
        heroes = heroes.filter(rarity_id__in=f_rarities)

    if f_families:
        f_families = f_families.split(',')
        if len([f for f in f_families if f not in families]):
            raise Http404("Invalid family filter")
        heroes = heroes.filter(Q(family_id__in=f_families) | Q(family__family_set_id__in=f_families))

    if f_class_types:
        f_class_types = f_class_types.split(',')
        if len([c for c in f_class_types if c not in class_types]):
            raise Http404("Invalid class filter")
        heroes = heroes.filter(class_type_id__in=f_class_types)

    emblem_annotated = False
    if f_emblems:
        f_emblems = f_emblems.split(',')
        if len([b for b in f_emblems if b not in class_types]):
            raise Http404("Invalid emblem filter")
        heroes = heroes.annotate(emblem_class_type_id=Case(
                                 When(parent_hero__isnull=False, then='parent_hero__class_type_id'),
                                 default='class_type_id'
                                 )).filter(emblem_class_type_id__in=f_emblems)
        emblem_annotated = True

    if f_mana_speeds:
        f_mana_speeds = f_mana_speeds.split(',')
        if len([m for m in f_mana_speeds if m not in mana_speeds]):
            raise Http404("Invalid mana speed filter")
        heroes = heroes.filter(mana_speed_id__in=f_mana_speeds)

    if f_costume:
        heroes = heroes.filter(parent_hero__isnull=(f_costume == 'N'))

    # Sorting options
    order_by_args = []
    if f_sort:
        f_sort = set(f_sort.split(','))
        SORTING_OPTIONS = {
            'element':    lambda: F('element__order').asc(nulls_last=True),
            'rarity':     lambda: '-rarity_id',
            'family':     lambda: F('family__order').asc(nulls_last=True),
            'class':      lambda: F('class_type_id').asc(nulls_last=True),
            'emblem':     lambda: F('emblem_class_type_id').asc(nulls_last=True),
            'mana_speed': lambda: 'mana_speed__max_mana',
        }
        if f_sort - SORTING_OPTIONS.keys():
            raise Http404("Invalid sorting options")
        if 'emblem' in f_sort and not emblem_annotated:
            heroes = heroes.annotate(emblem_class_type_id=Case(
                                     When(parent_hero__isnull=False, then='parent_hero__class_type_id'),
                                     default='class_type_id'))
        for sorting_option in f_sort:
            order_by_args.append(SORTING_OPTIONS[sorting_option]())

    if not order_by_args: # Default sorting options
        order_by_args = [F('can_be_received_date').desc(nulls_last=True), F('origin_id'), F('rarity_id').desc()]
    heroes = heroes.order_by(*order_by_args)

    return render(request, 'enpluzz_heroes/index.html', {
        'elements': elements,
        'rarities': rarities,
        'families': families,
        'class_types': class_types,
        'mana_speeds': mana_speeds,
        'f_elements': f_elements,
        'f_rarities': f_rarities,
        'f_families': f_families,
        'f_class_types': f_class_types,
        'f_emblems': f_emblems,
        'f_mana_speeds': f_mana_speeds,
        'f_costume': f_costume,
        'f_sort': f_sort,
        'heroes': heroes,
    })

def query(request):
    if request.method != 'POST':
        return redirect('enpluzz_heroes:index')

    f_elements = []
    f_rarities = []
    f_families = []
    f_class_types = []
    f_emblems = []
    f_mana_speeds = []
    f_costume = None

    for (k, v) in request.POST.items():
        if k == 'costume':
            if v in ('Y', 'N'):
                f_costume = v
        elif v == 'on':
            if k.startswith('element_'):
                f_elements.append(k[len('element_'):])
            if k.startswith('rarity_'):
                f_rarities.append(k[len('rarity_'):])
            if k.startswith('family_'):
                f_families.append(k[len('family_'):])
            if k.startswith('class_type_'):
                f_class_types.append(k[len('class_type_'):])
            if k.startswith('emblem_'):
                f_emblems.append(k[len('emblem_'):])
            if k.startswith('mana_speed_'):
                f_mana_speeds.append(k[len('mana_speed_'):])

    kwargs = dict()
    if f_elements:
        kwargs['f_elements'] = ','.join(f_elements)
    if f_rarities:
        kwargs['f_rarities'] = ','.join(f_rarities)
    if f_families:
        kwargs['f_families'] = ','.join(f_families)
    if f_class_types:
        kwargs['f_class_types'] = ','.join(f_class_types)
    if f_emblems:
        kwargs['f_emblems'] = ','.join(f_emblems)
    if f_mana_speeds:
        kwargs['f_mana_speeds'] = ','.join(f_mana_speeds)
    if f_costume:
        kwargs['f_costume'] = ','.join(f_costume)
    return redirect('enpluzz_heroes:query', **kwargs)

def hero(request, hero_id):
    hero = get_object_or_404(Hero, Q(can_be_received_date__lte=datetime.now(timezone.utc)) | Q(can_be_received_date=None), pk=hero_id, is_default_rider=False)
    return render(request, 'enpluzz_heroes/hero.html', {'hero': hero })

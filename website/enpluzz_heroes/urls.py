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

from django.urls import path, re_path

from . import views

app_name = 'enpluzz_heroes'
urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^s/(e:(?P<f_elements>[a-zA-Z,]+)/)?' \
                '(r:(?P<f_rarities>[0-9,]+)/)?' \
                '(f:(?P<f_families>[a-zA-Z,]+)/)?' \
                '(c:(?P<f_class_types>[a-zA-Z,]+)/)?' \
                '(b:(?P<f_emblems>[a-zA-Z,]+)/)?' \
                '(m:(?P<f_mana_speeds>[a-zA-Z,]+)/)?' \
                '(costume:(?P<f_costume>[YN])/)?$' \
            , views.index, name='index'),
    path('h/<int:hero_id>', views.hero, name='hero')
]

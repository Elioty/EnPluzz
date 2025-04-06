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

from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def enpLang(key, *args, **kwargs):
    #TODO: use the appropiate language
    if kwargs:
        return settings.ENP_LANGUAGES['English'].get('.'.join([key, *args]), kwargs)
    else:
        try:
            sep_index = args.index('|')
            return settings.ENP_LANGUAGES['English'].get('.'.join([key, *args[:sep_index]]), list(args[sep_index+1:]))
        except ValueError:
            return settings.ENP_LANGUAGES['English'].get('.'.join([key, *args]))

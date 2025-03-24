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

from django.core.management.base import BaseCommand, no_translations
from django.conf import settings
import zipfile
import json
from importlib import import_module
from enpluzz_core.modelHelper import DateTimeFieldFromJson, ForeignKeyFromJson, ManyToManyFieldFromJson
from datetime import datetime, timedelta
from collections.abc import Callable

def _get_object_type(typename:str) -> type:
    last_dot_pos = typename.rfind('.')
    module = import_module(typename[:last_dot_pos])
    return getattr(module, typename[last_dot_pos + 1:])

def _update_field(obj:any, field:str, value:any, to_save:bool) -> bool:
    if getattr(obj, field, None) != value:
        setattr(obj, field, value)
        return True
    else:
        return to_save

def _update_datetime_field(obj:any, field:DateTimeFieldFromJson, value: any, to_save:bool) -> bool:
    if value is None:
        value = field.get_default()
    elif isinstance(value, int):
        value = field.epoch_date + timedelta(seconds=value)
    elif isinstance(value, str):
        value = datetime.fromisoformat(value)
    else:
        raise Exception('Unexpected data type for a DateTimeFieldFromJson')
    return _update_field(obj, field.name, value, to_save)

def _update_foreignkey_field(obj:any, field:ForeignKeyFromJson, related_object_id: any, to_save:bool, write:Callable[[any, any, any], None]|None = None, second_pass:list|None = None) -> bool:
    related_object_type = field.remote_field.model
    def _get_default(field:ForeignKeyFromJson):
        if field.has_default():
            return related_object_type.objects.get(**{field.remote_field.field_name: field.get_default()})
        else:
            return None
    if related_object_id is not None:
        related_object_dict = {field.remote_field.field_name: related_object_id}
        try:
            related_object = related_object_type.objects.get(**related_object_dict)
        except related_object_type.DoesNotExist:
            if field.target_is_enumerate:
                related_object = related_object_type.objects.create(**related_object_dict)
                write and write('New enumerate {}({}).'.format(related_object_type.__name__, related_object_id))
            elif second_pass is not None:
                # Memorise it for second pass
                second_pass.append([obj, field, related_object_id])
                related_object = _get_default(field)
            else:
                raise
    else:
        related_object = _get_default(field)
    return _update_field(obj, field.name, related_object, to_save)

def _update_manytomany_field(obj:any, field: ManyToManyFieldFromJson, related_object_ids: list[any], write:Callable[[any, any, any], None]|None = None) -> None:
    source_object_type  = obj._meta.model
    related_object_type = field.remote_field.model
    related_object_list = []
    connection_type = field.remote_field.through
    connection_fields = [ None, None ]

    if field.remote_field.through_fields:
        connection_fields = [ connection_type._meta.get_field(field.remote_field.through_fields[0]), connection_type._meta.get_field(field.remote_field.through_fields[1]) ]
    else:
        for field2 in connection_type._meta.get_fields():
            rel = getattr(field2, "remote_field", None)
            if rel:
                if rel.model == related_object_type:
                    connection_fields[1] = field2
                    if connection_fields[0]: break
                elif rel.model == source_object_type:
                    connection_fields[0] = field2
                    if connection_fields[1]: break
        del field2, rel

    for related_object_id in related_object_ids:
        related_object_dict = {connection_fields[1].remote_field.field_name: related_object_id}
        try:
            related_object = related_object_type.objects.get(**related_object_dict)
        except related_object_type.DoesNotExist:
            if field.target_is_enumerate:
                related_object = related_object_type.objects.create(**related_object_dict)
                write and write('New enumerate {}({}).'.format(related_object_type.__name__, related_object_id))
            else:
                raise
        related_object_list.append(related_object)
    del related_object_dict

    for related_object in related_object_list:
        connection_object_dict = {connection_fields[0].name: obj, connection_fields[1].name: related_object}
        try:
            connection_object = connection_type.objects.get(**connection_object_dict)
        except connection_type.DoesNotExist:
            connection_type.objects.create(**connection_object_dict)

class Command(BaseCommand):
    help = 'Import a set of configuration and assets.'
    output_transaction = True

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('archive', type=str)

    @no_translations
    def handle(self, *args, **options):
        options['verbose'] and self.stdout.write('Importing archive "{}"...'.format(options['archive']))
        archive_file = zipfile.ZipFile(options['archive'], mode='r')

        options['verbose'] and self.stdout.write('Loading "override.json"...')
        with archive_file.open('override.json') as overrideFile:
            override = json.load(overrideFile)

        json_files = dict()
        second_pass = []
        for class_to_import in settings.CLASSES_TO_IMPORT_FROM_GAME_CONFIGURATION:
            options['verbose'] and self.stdout.write('Importing "{}" objects...'.format(class_to_import))

            # TODO: optimize this by checking the new file checksum against the previous one to avoid updating/creating objects of this class when not necessary
            object_type = _get_object_type(class_to_import)
            if not object_type.JsonMeta.source_file in json_files:
                options['verbose'] and self.stdout.write('Loading "cached_configurations/' + object_type.JsonMeta.source_file + '"...')
                with archive_file.open('cached_configurations/' + object_type.JsonMeta.source_file) as json_file:
                    json_files[object_type.JsonMeta.source_file] = json.load(json_file)

            elements_to_import = json_files[object_type.JsonMeta.source_file]
            for node_name in object_type.JsonMeta.data_path.split('.'):
                elements_to_import = elements_to_import[node_name]

            for element in elements_to_import:
                try:
                    obj = object_type.objects.get(**{object_type.JsonMeta.object_id_key: element[object_type.JsonMeta.data_id_key]})
                    new_object = False
                    to_save = False
                except object_type.DoesNotExist:
                    obj = object_type()
                    new_object = True
                    to_save = True

                for field in object_type._meta.get_fields():
                    if hasattr(field, 'json_field'):
                        if isinstance(field, DateTimeFieldFromJson): # Date time case
                            to_save = _update_datetime_field(obj, field, element.get(field.json_field, None), to_save)
                        elif isinstance(field, ForeignKeyFromJson):
                            to_save = _update_foreignkey_field(obj, field, element.get(field.json_field, None), to_save, self.stdout.write if options['verbose'] else None, second_pass)
                        elif isinstance(field, ManyToManyFieldFromJson):
                            if new_object:
                                # Memorise it for second pass, cannot make a many-to-many relationship yet
                                second_pass.append([obj, field, element.get(field.json_field, [])])
                                continue
                            _update_manytomany_field(obj, field, element.get(field.json_field, []), self.stdout.write if options['verbose'] else None)
                        else: # General case
                            to_save = _update_field(obj, field.name, element.get(field.json_field, field.get_default()), to_save)

                if to_save:
                    obj.save()
                    new_object and options['verbose'] and self.stdout.write('New object {}.'.format(element[object_type.JsonMeta.data_id_key]))
                    not new_object and options['verbose'] and self.stdout.write('Updated object {}.'.format(element[object_type.JsonMeta.data_id_key]))

                reverse_relationships = getattr(object_type.JsonMeta, 'reverse_relationships', [])
                if len(reverse_relationships):
                    for reverse_relationship in reverse_relationships:
                        to_object_type = _get_object_type(reverse_relationship['to'])
                        for object_id_key in element[reverse_relationship['data_field']]:
                            to_obj = to_object_type.objects.get(**{reverse_relationship['object_id_key']: object_id_key})
                            if _update_field(to_obj, reverse_relationship['to_field'], obj, False):
                                to_obj.save()

            self.stdout.write(self.style.SUCCESS('"{}" objects imported successfully.'.format(class_to_import)))

        if second_pass:
            options['verbose'] and self.stdout.write('Second pass for missing references...')
            for entry in second_pass:
                to_save = False
                obj, field, value = entry
                if isinstance(field, ForeignKeyFromJson):
                    to_save = _update_foreignkey_field(obj, field, value, to_save, self.stdout.write if options['verbose'] else None)
                elif isinstance(field, ManyToManyFieldFromJson):
                    _update_manytomany_field(obj, field, value, self.stdout.write if options['verbose'] else None)

                if to_save:
                    obj.save()
                    options['verbose'] and self.stdout.write('Updated object {}.'.format(getattr(obj, type(obj).JsonMeta.object_id_key)))

        options['verbose'] and self.stdout.write('Saving the archive files...'.format(options['archive']))
        for member in archive_file.infolist():
            # TODO: optimize this by checking the new file checksum against the previous one to avoid extracting if it still matches, and print when updating a file (in verbose mode)
            archive_file.extract(member, settings.BASE_DIR / 'enpluzz_core' / 'game_data')

        # Other things that do not need to be in the database
        other_settings = dict()
        for source_file in ['battle.json', 'other.json']:
            if not source_file in json_files:
                options['verbose'] and self.stdout.write('Loading "cached_configurations/' + source_file + '"...')
                with archive_file.open('cached_configurations/' + source_file) as json_file:
                    json_files[source_file] = json.load(json_file)

        other_settings['statsPerLevelConfiguration'] = json_files['battle.json']['battleConfig']['statsPerLevelConfiguration']
        other_settings['heroPowerBonusPerRarity'] = json_files['battle.json']['battleConfig']['heroPowerBonusPerRarity']
        other_settings['heroPowerAttackWeightPerMil'] = json_files['battle.json']['battleConfig']['heroPowerAttackWeightPerMil']
        other_settings['heroPowerDefenseWeightPerMil'] = json_files['battle.json']['battleConfig']['heroPowerDefenseWeightPerMil']
        other_settings['heroPowerHealthWeightPerMil'] = json_files['battle.json']['battleConfig']['heroPowerHealthWeightPerMil']
        other_settings['heroPowerSpecialBonusPerLevel'] = json_files['battle.json']['battleConfig']['heroPowerSpecialBonusPerLevel']
        other_settings['heroPowerBonusPerTalentNode'] = json_files['battle.json']['battleConfig']['heroPowerBonusPerTalentNode']
        other_settings['dragonPowerSpecialBonusPerLevel'] = json_files['battle.json']['battleConfig']['dragonPowerSpecialBonusPerLevel']
        other_settings['dragonPowerBonusPerRarity'] = json_files['battle.json']['battleConfig']['dragonPowerBonusPerRarity']
        other_settings['heroLevelUp'] = json_files['other.json']['otherConfig']['logic']['heroLevelUp']
        other_settings['dragonLevelUp'] = json_files['other.json']['otherConfig']['logic']['dragonLevelUp']
        other_settings['troopLevelUp'] = json_files['other.json']['otherConfig']['logic']['troopLevelUp']

        with open(settings.BASE_DIR / 'enpluzz_core' / 'game_data' / 'game_settings.json', mode='w+', encoding='UTF-8') as game_settings_file:
            json.dump(other_settings, game_settings_file)

        self.stdout.write(self.style.SUCCESS('Game files saved successfully.'))

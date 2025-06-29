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
from enpluzz_core.modelHelper import *
from enpluzz_core.models import Element, Rarity
from enpluzz_heroes.models import Origin, ManaSpeed, SpecialSkill, TrainerType
from django.core.files.storage import default_storage
from django.conf import settings

class DragonSpiritBonusType(models.Model):
    enp_id = models.CharField(max_length=255, unique=True)

    class JsonMeta:
        is_enumerate = True

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class DragonSpiritBonus(models.Model):
    enp_id       = CharFieldFromJson(json_field='id', max_length=255, unique=True)
    bonus_type   = ForeignKeyFromJson(DragonSpiritBonusType, json_field='bonusType', to_field='enp_id', on_delete=models.PROTECT)

    def _default_stat_bonuses() -> list:
        return [{'bonusLevels': []}] * 5
    stat_bonuses = JSONFieldFromJson(json_field='statBonuses', default=_default_stat_bonuses)

    class JsonMeta:
        source_file   = 'battle.json'
        data_path     = 'battleConfig.dragonSpiritBonuses'
        data_id_key   = 'id'
        object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

class AssistSkill(models.Model):
    enp_id       = CharFieldFromJson(json_field='id', max_length=255, unique=True)
    # TODO: other fields

    class JsonMeta:
        source_file   = 'battle.json'
        data_path     = 'battleConfig.assistSkills'
        data_id_key   = 'id'
        object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

class Dragon(models.Model):
    enp_id       = CharFieldFromJson(json_field='id', max_length=255, unique=True)
    element      = ForeignKeyFromJson(Element, json_field='element', to_field='enp_id', on_delete=models.PROTECT)
    rarity       = ForeignKeyFromJson(Rarity, json_field='rarity', to_field='enp_id', on_delete=models.PROTECT)
    origin       = ForeignKeyFromJson(Origin, json_field='origin', to_field='enp_id', on_delete=models.PROTECT, null=True)
    trainer_type = ForeignKeyFromJson(TrainerType, json_field='trainerType', to_field='enp_id', on_delete=models.PROTECT, null=True)

    mana_speed    = ForeignKeyFromJson(ManaSpeed, json_field='manaSpeedId', to_field='enp_id', on_delete=models.PROTECT, null=True, related_name='dragons')

    special_skill = ForeignKeyFromJson(SpecialSkill, json_field='specialId', to_field='enp_id', on_delete=models.PROTECT, null=True)

    can_be_received_date = DateTimeFieldFromJson(json_field='canBeReceivedDate', null=True)

    dragon_spirit_class_bonuses   = ForeignKeyFromJson(DragonSpiritBonus, json_field='dragonSpiritClassBonusesId', to_field='enp_id', on_delete=models.PROTECT, null=True, related_name='+')
    dragon_spirit_element_bonuses = ForeignKeyFromJson(DragonSpiritBonus, json_field='dragonSpiritElementBonusesId', to_field='enp_id', on_delete=models.PROTECT, null=True, related_name='+')

    assist_skill            = ForeignKeyFromJson(AssistSkill, json_field='assistSkillId', to_field='enp_id', on_delete=models.PROTECT, null=True, related_name='+')
    assist_skill_mana_speed = ForeignKeyFromJson(ManaSpeed, json_field='assistSkillManaSpeedId', to_field='enp_id', on_delete=models.PROTECT, null=True, related_name='+')

    base_attack  = IntegerFieldFromJson(json_field='baseAttack', default=0)
    base_defense = IntegerFieldFromJson(json_field='baseDefense', default=0)
    base_health  = IntegerFieldFromJson(json_field='baseHealth', default=0)

    class JsonMeta:
        source_file   = 'characters.json'
        data_path     = 'charactersConfig.dragons'
        data_id_key   = 'id'
        object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

    def sprite_name(self) -> str:
        sprite_name = 'misc/missing_graphics.png'
        if self.trainer_type_id is not None:
            if self.trainer_type_id == 'Normal':
                sprite_name = 'dragons/trainer_dragon_' + self.element_id.lower() +'.png'
            elif self.trainer_type_id == 'NoviceRainbow':
                sprite_name = 'dragons/trainer_dragon_rainbow_novice.png'
        else:
            sprite_name = 'dragons/' + self.enp_id + '.png'
        # TODO: better manage the path to the game data via a setting
        if not default_storage.exists('enpluzz_core/game_data/assets_extract/' + sprite_name):
            sprite_name = 'misc/missing_graphics.png'
        return sprite_name

    def name_lang_key(self) -> str:
        if self.trainer_type_id is not None:
            if self.trainer_type_id == 'Normal':
                key = 'trainer'
            elif self.trainer_type_id == 'NoviceRainbow':
                key = 'trainer_rainbow_novice'
        else:
            key = self.enp_id
        return 'dragons.name.' + key

    #TODO: this method would probably rather be an helper function in enpluzz_core
    def stats(self, ascension:int=-1, level:int=-1, special_skill_level:int=-1) -> tuple[int, int, int, int]:
        if self.trainer_type_id is not None:
            power = settings.ENP_SETTINGS['dragonPowerBonusPerRarity'][self.rarity_id - 1] \
                  + (self.base_attack * settings.ENP_SETTINGS['heroPowerAttackWeightPerMil'] + self.base_defense * settings.ENP_SETTINGS['heroPowerDefenseWeightPerMil'] + self.base_health * settings.ENP_SETTINGS['heroPowerHealthWeightPerMil']) // 1000
            return (self.base_attack, self.base_defense, self.base_health, power)

        per_ascension_level_parameters = settings.ENP_SETTINGS['dragonLevelUp']['parametersPerAscensionLevelPerRarity'][self.rarity_id - 1]['parameters']
        if ascension == -1:
            ascension = len(per_ascension_level_parameters)
        if level == -1:
            level = per_ascension_level_parameters[ascension - 1]['maxLevel']
        if special_skill_level == -1:
            special_skill_level = self.special_skill.max_level

        internal_level = 1
        levels_on_upgrade = 0
        for ascension_level in range(ascension):
            internal_level += per_ascension_level_parameters[ascension_level]['maxLevel'] - 1 + levels_on_upgrade
            levels_on_upgrade = per_ascension_level_parameters[ascension_level].get('levelsIncreasedOnUpgrade', 0)

        attack  = self.base_attack  * (1000 + (internal_level - 1) * settings.ENP_SETTINGS['statsPerLevelConfiguration']['dragonAttackStatMultipliersPerLevelPerMil'][self.rarity_id - 1]) // 1000
        defense = self.base_defense * (1000 + (internal_level - 1) * settings.ENP_SETTINGS['statsPerLevelConfiguration']['dragonDefenseStatMultipliersPerLevelPerMil'][self.rarity_id - 1]) // 1000
        health  = self.base_health  * (1000 + (internal_level - 1) * settings.ENP_SETTINGS['statsPerLevelConfiguration']['dragonHealthStatMultipliersPerLevelPerMil'][self.rarity_id - 1]) // 1000

        power = settings.ENP_SETTINGS['dragonPowerBonusPerRarity'][self.rarity_id - 1] \
              + (attack * settings.ENP_SETTINGS['heroPowerAttackWeightPerMil'] + defense * settings.ENP_SETTINGS['heroPowerDefenseWeightPerMil'] + health * settings.ENP_SETTINGS['heroPowerHealthWeightPerMil']) // 1000 \
              + (special_skill_level - 1) * settings.ENP_SETTINGS['dragonPowerSpecialBonusPerLevel']

        return (attack, defense, health, power)
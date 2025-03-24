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
from django.core.files.storage import default_storage
from django.conf import settings

class Origin(models.Model):
    enp_id = models.CharField(max_length=255, unique=True)
    order  = models.IntegerField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class FamilySet(models.Model):
    enp_id = CharFieldFromJson(json_field='id', max_length=255, unique=True)

    class JsonMeta:
        source_file   = 'battle.json'
        data_path     = 'battleConfig.familySets'
        data_id_key   = 'id'
        object_id_key = 'enp_id'
        reverse_relationships = [
            {'data_field': 'families', 'object_id_key': 'enp_id', 'to': 'enpluzz_heroes.models.Family', 'to_field': 'family_set'},
        ]

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class Family(models.Model):
    enp_id                                = CharFieldFromJson(json_field='id', max_length=255, unique=True)
    deactivated_until                     = DateTimeFieldFromJson(json_field='deactivatedUntil', null=True)
    hidden_until                          = DateTimeFieldFromJson(json_field='hiddenUntil', null=True)
    is_realm                              = BooleanFieldFromJson(json_field='isRealm', default=False)
    use_custom_realm_description          = BooleanFieldFromJson(json_field='useCustomRealmDescription', default=False)
    active_on_fully_ascended_members_only = BooleanFieldFromJson(json_field='activeOnFullyAscendedMembersOnly', default=False)
    #TODO: familyEffects

    family_set = models.ForeignKey(FamilySet, to_field='enp_id', on_delete=models.SET_NULL, null=True)
    order      = models.IntegerField(default=None, null=True)

    class JsonMeta:
        source_file   = 'battle.json'
        data_path     = 'battleConfig.families'
        data_id_key   = 'id'
        object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

    def _family_id(self) -> str:
        return self.enp_id if self.family_set_id is None else self.family_set_id

    def sprite_name(self) -> str:
        sprite_name = 'families/' + self._family_id() + '.png'
        # TODO: better manage the path to the game data via a setting
        if not default_storage.exists('enpluzz_core/game_data/assets_extract/' + sprite_name):
            sprite_name = 'misc/missing_graphics.png'
        return sprite_name

    def name(self) -> str:
        family_lang_key = self._family_id()
        if family_lang_key.startswith('hotm'):
            return settings.ENP_LANGUAGES['English'].get('herocard.family.title.hotm', [family_lang_key[4:]])
        else:
            return settings.ENP_LANGUAGES['English'].get('herocard.family.title.' + family_lang_key)

class TrainerType(models.Model):
    enp_id = models.CharField(max_length=255, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class ClassType(models.Model):
    enp_id  = CharFieldFromJson(json_field='classType', max_length=255, unique=True)
    talent_skill_act_per_mil_per_node = IntegerFieldFromJson(json_field='talentSkillActivationPerMilPerNode', default=0)
    improved_talent_skill_act_per_mil_per_node = IntegerFieldFromJson(json_field='improvedTalentSkillActivationPerMilPerNode', default=0)

    class JsonMeta:
        source_file   = 'other.json'
        data_path     = 'otherConfig.logic.heroClass.classTalents'
        data_id_key   = 'classType'
        object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

    def name_lang_key(self) -> str:
        return 'hero.class.' + self.enp_id.lower()

class ManaSpeed(models.Model):
    enp_id                            = CharFieldFromJson(json_field='id', max_length=255, unique=True)
    max_mana                          = IntegerFieldFromJson(json_field='maxMana', default=0)
    alternating_mana_modifier_per_mil = IntegerFieldFromJson(json_field='alternatingManaModifierPerMil', default=0)
    charged_mana_modifiers_per_mil    = JSONFieldFromJson(json_field='chargedManaModifiersPerMil', default=list)
    show_extra_info                   = BooleanFieldFromJson(json_field='showExtraInfo', default=False)

    order  = models.IntegerField(default=None, null=True)

    class JsonMeta:
        source_file   = 'battle.json'
        data_path     = 'battleConfig.manaSpeeds'
        data_id_key   = 'id'
        object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

    def name_lang_key(self) -> str:
        return 'manaspeed.' + self.enp_id.lower()

class CostumeBonus(models.Model):
    enp_id = CharFieldFromJson(json_field='id', max_length=255, unique=True)

    def _default_stat_bonuses() -> list:
        return [{'bonusLevels': []}] * 5
    stat_bonuses = JSONFieldFromJson(json_field='statBonuses', default=_default_stat_bonuses)

    class JsonMeta:
        source_file   = 'other.json'
        data_path     = 'otherConfig.logic.costumes.costumeBonuses'
        data_id_key   = 'id'
        object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class AetherGifts(models.Model):
    enp_id = CharFieldFromJson(json_field='id', max_length=255, unique=True)
    # aetherGiftType is always set to StatusEffectAtStartOfNewWave
    # TODO: status effect
    # turnsIncrementPerLevel is always set to 0

    class JsonMeta:
            source_file   = 'battle.json'
            data_path     = 'battleConfig.aetherGifts'
            data_id_key   = 'id'
            object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def name_lang_key(self) -> str:
        return 'limitbreak.gift.title.' + self.enp_id.lower()

class SpecialSkill(models.Model):
    enp_id = CharFieldFromJson(json_field='id', max_length=255, unique=True)
    # TODO: many fields to add
    max_level = IntegerFieldFromJson(json_field='maxLevel', default=0)

    class JsonMeta:
            source_file   = 'specials.json'
            data_path     = 'specialsConfig.characterSpecials'
            data_id_key   = 'id'
            object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def name_lang_key(self) -> str:
        return 'specials.name.' + self.enp_id.lower()

class Hero(models.Model):
    enp_id       = CharFieldFromJson(json_field='id', max_length=255, unique=True)
    element      = ForeignKeyFromJson(Element, json_field='element', to_field='enp_id', target_is_enumerate=True, on_delete=models.PROTECT)
    rarity       = ForeignKeyFromJson(Rarity, json_field='rarity', to_field='enp_id', target_is_enumerate=True, on_delete=models.PROTECT)
    origin       = ForeignKeyFromJson(Origin, json_field='origin', to_field='enp_id', target_is_enumerate=True, on_delete=models.PROTECT, null=True)
    trainer_type = ForeignKeyFromJson(TrainerType, json_field='trainerType', to_field='enp_id', target_is_enumerate=True, on_delete=models.PROTECT, null=True)

    family = ForeignKeyFromJson(Family, json_field='family', to_field='enp_id', on_delete=models.PROTECT, null=True)

    class_type                = ForeignKeyFromJson(ClassType, json_field='classType', to_field='enp_id', on_delete=models.PROTECT, null=True)
    has_improved_talent_skill = BooleanFieldFromJson(json_field='hasImprovedTalentSkill', default=False)

    aether_gift   = ForeignKeyFromJson(AetherGifts, json_field='aetherGift', to_field='enp_id', on_delete=models.PROTECT, null=True)

    mana_speed    = ForeignKeyFromJson(ManaSpeed, json_field='manaSpeedId', to_field='enp_id', on_delete=models.PROTECT, null=True)

    special_skill = ForeignKeyFromJson(SpecialSkill, json_field='specialId', to_field='enp_id', on_delete=models.PROTECT, null=True)
    # TODO: passive skills and costume passive skills

    can_be_received_date = DateTimeFieldFromJson(json_field='canBeReceivedDate', null=True)

    costume_bonus = ForeignKeyFromJson(CostumeBonus, json_field='costumeBonusesId', to_field='enp_id', on_delete=models.PROTECT, default='default', related_name='+')
    parent_hero   = ForeignKeyFromJson('self', json_field='parentHeroId', to_field='enp_id', on_delete=models.PROTECT, null=True, related_name='costumes')

    is_default_rider = BooleanFieldFromJson(json_field='isDefaultRider', default=False)

    base_attack  = IntegerFieldFromJson(json_field='baseAttack', default=0)
    base_defense = IntegerFieldFromJson(json_field='baseDefense', default=0)
    base_health  = IntegerFieldFromJson(json_field='baseHealth', default=0)

    class JsonMeta:
            source_file   = 'characters.json'
            data_path     = 'charactersConfig.heroes'
            data_id_key   = 'id'
            object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
            models.Index(fields=['parent_hero']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

    def sprite_name(self) -> str:
        sprite_name = 'misc/missing_graphics.png'
        if self.trainer_type_id is not None:
            if self.trainer_type_id == 'Normal':
                sprite_name = 'heroes/trainer_' + self.element_id.lower() +'.png'
            elif self.trainer_type_id == 'MasterRainbow':
                sprite_name = 'heroes/trainer_rainbow.png'
        else:
            sprite_name = 'heroes/' + self.enp_id + '.png'
        # TODO: better manage the path to the game data via a setting
        if not default_storage.exists('enpluzz_core/game_data/assets_extract/' + sprite_name):
            sprite_name = 'misc/missing_graphics.png'
        return sprite_name

    def name_lang_key(self) -> str:
        if self.trainer_type_id is not None:
            if self.trainer_type_id == 'Normal':
                key = 'trainer'
            elif self.trainer_type_id == 'MasterRainbow':
                key = 'trainer_rainbow'
        else:
            if self.parent_hero is not None:
                key = self.parent_hero_id
            else:
                key = self.enp_id
        return 'heroes.name.' + key

    def costume_index(self) -> int|None:
        if self.parent_hero is None:
            if len(self.costumes.all()) > 0: return 0
            else: return None
        else:
            costumes_list = list(self.parent_hero.costumes.all())
            costumes_list.sort(key=lambda c: c.can_be_received_date)
            return costumes_list.index(self) + 1

    #TODO: this method would probably rather be an helper function in enpluzz_core
    def stats(self, ascension:int=-1, limit_break:int=0, level:int=-1, special_skill_level:int=-1) -> tuple[int, int, int, int]:
        if self.trainer_type_id is not None or self.is_default_rider:
            power = settings.ENP_SETTINGS['heroPowerBonusPerRarity'][self.rarity_id - 1] \
                  + (self.base_attack * settings.ENP_SETTINGS['heroPowerAttackWeightPerMil'] + self.base_defense * settings.ENP_SETTINGS['heroPowerDefenseWeightPerMil'] + self.base_health * settings.ENP_SETTINGS['heroPowerHealthWeightPerMil']) // 1000
            return (self.base_attack, self.base_defense, self.base_health, power)

        per_ascension_level_parameters = settings.ENP_SETTINGS['heroLevelUp']['parametersPerAscensionLevelPerRarity'][self.rarity_id - 1]['parameters']
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

        attack  = self.base_attack  * (1000 + (internal_level - 1) * settings.ENP_SETTINGS['statsPerLevelConfiguration']['attackStatMultipliersPerLevelPerMil'][self.rarity_id - 1]) // 1000
        defense = self.base_defense * (1000 + (internal_level - 1) * settings.ENP_SETTINGS['statsPerLevelConfiguration']['defenseStatMultipliersPerLevelPerMil'][self.rarity_id - 1]) // 1000
        health  = self.base_health  * (1000 + (internal_level - 1) * settings.ENP_SETTINGS['statsPerLevelConfiguration']['healthStatMultipliersPerLevelPerMil'][self.rarity_id - 1]) // 1000

        # TODO: limitbreak

        costume_index = self.costume_index()
        if costume_index is not None and costume_index > 0:
            bonus_level = 0
            if costume_index > 1:
                bonus_level = (costume_index - 1) * len(per_ascension_level_parameters)
            bonus_level += ascension - 1
            if ascension == len(per_ascension_level_parameters) and level >= per_ascension_level_parameters[ascension - 1]['maxLevel']:
                bonus_level += 1
            stat_bonus = self.parent_hero.costume_bonus.stat_bonuses[self.rarity_id - 1]['bonusLevels'][bonus_level - 1]

            attack  = attack  * (1000 + stat_bonus['attackBonusPerMil']) // 1000
            defense = defense * (1000 + stat_bonus['defenseBonusPerMil']) // 1000
            health  = health  * (1000 + stat_bonus['healthBonusPerMil']) // 1000

        power = settings.ENP_SETTINGS['heroPowerBonusPerRarity'][self.rarity_id - 1] \
              + (attack * settings.ENP_SETTINGS['heroPowerAttackWeightPerMil'] + defense * settings.ENP_SETTINGS['heroPowerDefenseWeightPerMil'] + health * settings.ENP_SETTINGS['heroPowerHealthWeightPerMil']) // 1000 \
              + (special_skill_level - 1) * settings.ENP_SETTINGS['heroPowerSpecialBonusPerLevel']

        return (attack, defense, health, power)

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
from enpluzz_core.models import GameMode, Rarity
from enpluzz_heroes.models import Hero, ClassType

class ItemType(models.Model):
    enp_id = models.CharField(max_length=255, unique=True)
    order  = models.IntegerField(default=None, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class RefillType(models.Model):
    enp_id = models.CharField(max_length=255, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class TomeType(models.Model):
    enp_id = models.CharField(max_length=255, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class Item(models.Model):
    enp_id     = CharFieldFromJson(json_field='id', max_length=255, unique=True)
    item_type  = ForeignKeyFromJson(ItemType, json_field='itemType', to_field='enp_id', target_is_enumerate=True, on_delete=models.PROTECT, null=True)
    game_modes = ManyToManyFieldFromJson(GameMode, json_field='gameModes', target_is_enumerate=True, through='ItemToGameMode')
    rarity     = ForeignKeyFromJson(Rarity, json_field='rarity', to_field='enp_id', target_is_enumerate=True, on_delete=models.PROTECT, null=True, related_name='+')
    gem_value  = IntegerFieldFromJson(json_field='gemValue', null=True)
    order      = models.IntegerField(default=None, null=True)

    not_allowed_as_loot  = BooleanFieldFromJson(json_field='notAllowedAsLoot', default=False)
    can_be_received_date = DateTimeFieldFromJson(json_field='canBeReceivedDate', null=True)

    # When item_type is Costume
    costume     = ForeignKeyFromJson(Hero, json_field='costumeId', to_field='enp_id', on_delete=models.PROTECT, null=True, related_name='+')
    parent_hero = ForeignKeyFromJson(Hero, json_field='parentHeroId', to_field='enp_id', on_delete=models.PROTECT, null=True, related_name='+')

    # When item_type is xxxRefill
    refill_type   = ForeignKeyFromJson(RefillType, json_field='typeOfRefill', to_field='enp_id', target_is_enumerate=True, on_delete=models.PROTECT, null=True)
    # Ignore typeOfRefillAmount, it is always set to "Specific" when the actual amount is not None.
    refill_amount = IntegerFieldFromJson(json_field='refillAmount', null=True)

    # When item_type is Collection
    #TODO: givenItemId => foreign key to another item
    given_item_amount = IntegerFieldFromJson(json_field='givenItemAmount', null=True)

    # When item_type is Tome
    tome_type = ForeignKeyFromJson(TomeType, json_field='typeOfTome', to_field='enp_id', target_is_enumerate=True, on_delete=models.PROTECT, null=True)
    # For LevelUp tomes
    effect_amount             = IntegerFieldFromJson(json_field='effectAmount', null=True)
    increase_special_level    = BooleanFieldFromJson(json_field='increaseSpecialLevel', default=False)
    limit_break_effect_amount = IntegerFieldFromJson(json_field='limitBreakEffectAmount', null=True)
    rewards_per_element       = JSONFieldFromJson(json_field='rewardsPerElement', null=True)
    rewards_only_for_limit_broken_characters = BooleanFieldFromJson(json_field='rewardsOnlyForLimitBrokenCharacters', default=False)
    # For LimitBreak tomes
    targeted_limit_break_level = IntegerFieldFromJson(json_field='targetedLimitBreakLevel', null=True)

    # When item_type is LotteryToken
    amount_for_summon    = IntegerFieldFromJson(json_field='amountForSummon', null=True)
    amount_for_10_summon = IntegerFieldFromJson(json_field='amountFor10Summon', null=True)
    guaranteed_rarity    = ForeignKeyFromJson(Rarity, json_field='guaranteedRarity', to_field='enp_id', target_is_enumerate=True, on_delete=models.PROTECT, null=True, related_name='+')

    # When item_type is AscensionMaterial or ItemCrafting
    first_province         = IntegerFieldFromJson(json_field='firstProvince', null=True)
    province_reward_weight = IntegerFieldFromJson(json_field='provinceRewardWeight', null=True)

    # When item_type is Battle or TitanBattle
    #TODO

    # When item_type is HeroEmblem
    hero_class = ForeignKeyFromJson(ClassType, json_field='heroClass', to_field='enp_id', on_delete=models.PROTECT, null=True)

    # When item_type is Relic
    #TODO

    # When item_type is TimeSkip
    amount_in_seconds = IntegerFieldFromJson(json_field='amountInSeconds', null=True)

    class JsonMeta:
        source_file   = 'other.json'
        data_path     = 'otherConfig.logic.inventory.items'
        data_id_key   = 'id'
        object_id_key = 'enp_id'

    class Meta:
        indexes = [
            models.Index(fields=['enp_id']),
        ]

    def __str__(self) -> str:
        return str(self.enp_id)

class ItemToGameMode(models.Model):
    item = models.ForeignKey(Item, to_field='enp_id', on_delete=models.CASCADE, related_name='+')
    game_mode = models.ForeignKey(GameMode, to_field='enp_id', on_delete=models.CASCADE, related_name='+')

    class Meta:
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['game_mode']),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=['item', 'game_mode'], name="unique_item_to_game_mode"
            )
        ]

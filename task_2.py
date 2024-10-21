from datetime import date
import csv

from django.db import transaction, models


class Player(models.Model):
    player_id = models.CharField(max_length=100)


class Level(models.Model):
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class Prize(models.Model):
    title = models.CharField()


class PlayerLevel(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed = models.DateField()
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)


class LevelPrize(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    received = models.DateField()


class LevelIsNotCompletedException(BaseException):
    pass


class PlayerDoesNotExist(BaseException):
    pass


class PrizeDoesNotExist(BaseException):
    pass


def assign_prize_to_player(player_id: int, level_id: int, prize_id: int) -> None:
    with transaction.atomic():
        player_level = PlayerLevel.objects.get(player_id=player_id, level_id=level_id)
        prize = Prize.objects.get(id=prize_id)
        level = Level.objects.get(id=level_id)

        if not player_level.is_completed:
            raise LevelIsNotCompletedException

        LevelPrize.objects.create(
            level=level,
            prize=prize,
            received=date.today()
        )


def export_player_level_data_to_csv(file_path='player_level_data.csv') -> str:
    data = [['Player ID', 'Level Title', 'Is Completed', 'Prize']]

    player_levels = PlayerLevel.objects.select_related('player', 'level').prefetch_related('level__levelprize_set')
    for player_level in player_levels.iterator():
        prizes = LevelPrize.objects.filter(level=player_level.level).values_list('prize__title', flat=True)
        prize_list = ", ".join(prizes)

        data.append([
            player_level.player.player_id,
            player_level.level.title,
            "Yes" if player_level.is_completed else "No",
            prize_list
        ])

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    return file_path

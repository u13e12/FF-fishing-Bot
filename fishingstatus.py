import enum


class FishingStatus(enum.Enum):
    Fishing = 1
    Reeling = 2
    Success = 3
    Failure = 4
    ReturnFish = 5
    ChangeBait = 6
    ChangeLocation = 7
    Exit = 8
    Idle = 9
    Mooching = 10

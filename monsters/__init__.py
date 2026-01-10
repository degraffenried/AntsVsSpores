from .base import Monster
from .walker import Walker
from .flyer import Flyer
from .spider import Spider
from .blob import Blob
from .taterbug import Taterbug
from .chompy import Chompy
from .snake import Snake
from .shriek import Shriek


def create_monster(data):
    monster_type = data.get('type', 'walker')
    if monster_type == 'walker':
        return Walker(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'])
    elif monster_type == 'flyer':
        return Flyer(data['x'], data['y'], data['patrol_range'],
                    data['speed'], data['health'])
    elif monster_type == 'spider':
        return Spider(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'])
    elif monster_type == 'blob':
        return Blob(data['x'], data['y'], data['patrol_range'],
                   data['speed'], data['health'])
    elif monster_type == 'taterbug':
        return Taterbug(data['x'], data['y'], data['patrol_range'],
                        data['speed'], data['health'])
    elif monster_type == 'chompy':
        return Chompy(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'])
    elif monster_type == 'snake':
        return Snake(data['x'], data['y'], data['patrol_range'],
                    data['speed'], data['health'],
                    data.get('aggro_duration', 180))
    elif monster_type == 'shriek':
        return Shriek(data['x'], data['y'], data['patrol_range'],
                     data['speed'], data['health'],
                     data.get('aggro_duration', 180))
    return None


__all__ = [
    'Monster',
    'Walker',
    'Flyer',
    'Spider',
    'Blob',
    'Taterbug',
    'Chompy',
    'Snake',
    'Shriek',
    'create_monster',
]

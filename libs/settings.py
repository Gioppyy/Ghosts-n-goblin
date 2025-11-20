import json, os

class Settings:
    def __init__(self, config_path=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if config_path is None:
            config_path = os.path.join(base_dir, "config.json")

        with open(config_path, "r") as f:
            self._config = json.load(f)

    # Images
    def get_img(self, key):
        return self._config['imgs'].get(key)

    def get_sprite_sheet(self):
        return self._config['imgs']['sprites']

    # Audio
    def get_audio(self, key):
        return self._config['audio'].get(key)

    # Keys
    def get_key(self, action):
        return self._config['keys'].get(action)

    def get_all_keys(self):
        return self._config['keys']

    # Game settings
    def get_game_setting(self, *keys):
        result = self._config['game']
        for key in keys:
            result = result[key]
        return result

    def get_bg_size(self):
        return (self._config['game']['background']['width'],
                self._config['game']['background']['height'])

    def get_view_size(self):
        return (self._config['game']['view']['width'],
                self._config['game']['view']['height'])

    def get_initial_lives(self):
        return self._config['game']['lives']['initial']

    def get_song_change_x(self):
        return self._config['game']['song_change_x']

    # Level data
    def get_level_data(self, key):
        return self._config['level'].get(key)

    def get_platforms(self):
        return self._config['level']['platforms']

    def get_gravestones(self):
        return self._config['level']['gravestones']

    def get_plants(self):
        return self._config['level']['plants']

    def get_ladders(self):
        return self._config['level']['ladders']

    def get_arthur_start(self):
        return tuple(self._config['level']['arthur_start'])

    # Actor settings
    def get_actor_config(self, actor_name):
        return self._config.get(actor_name, {})

    def get_animation_data(self, actor_name, animation_name):
        actor_config = self._config.get(actor_name, {})
        animations = actor_config.get('animations', {})
        anim_data = animations.get(animation_name, {})

        # Convert lists to tuples for frames
        if 'frames' in anim_data:
            frames = [tuple(map(tuple, frame)) for frame in anim_data['frames']]
            return {
                'frames': frames,
                'speed': anim_data.get('speed', 5),
                'loop': anim_data.get('loop', True)
            }
        return None

    # Zombie spawn settings
    def get_zombie_spawn_config(self):
        return self._config['game']['zombie_spawn']

    # Gameover
    def get_gameover_config(self):
        return self._config['gameover']

    def get_gamewin_config(self):
        return self._config['gamewin']

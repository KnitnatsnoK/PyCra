from assets import *
from value_assets import *

pg.mixer.set_num_channels(64)

THREAD_KILLERS:dict[str, bool] = {}
def create_Thread(target, args):
    thread = threading.Thread(target=target, args=args)
    THREAD_KILLERS[thread.name] = False
    thread.start()
    return thread.name

class Sound_Channel:
    free_channels = [i for i in range(pg.mixer.get_num_channels())]
    def __init__(self, name:str):
        self.id = Sound_Channel.free_channels[0]
        Sound_Channel.free_channels.remove(self.id)
        self.channel = pg.Channel(self.id)
        self.name = name
        self.volume = 0

    def play(self, sound:pg.Sound|str, loops:int=0, fade_ms:int=0, pitch:float=1.0, position:float=None, volumes:tuple[float, float]=(1.0, 1.0)):
        sound = SOUNDS[sound] if isinstance(sound, str) else sound
        duration = sound.get_length()
        if pitch != 1.0:
            sound, duration = pitch_sound(sound, pitch)
        if position != 0.0:
            sound = stereoize_sound(sound, position, *volumes)
        self.channel.play(sound, loops, fade_ms=fade_ms)
        return duration

    def delete(self):
        Sound_Channel.free_channels.append(self.id)
        SOUND_CHANNELS.pop(self.name)

class Music_Player:
    def __init__(self, name:str, playlist:list[str|pg.Sound], channel_name:str="default"):
        self.name = name
        self.playlist = playlist
        self.channel_name = channel_name

        self.player_thread_name:str = None

    def play(self, loops:int=-1, fade_ms:int=0, fadeout_ms:int=0, add_fade_time:bool=False, add_fadeout_time:bool=False, position:float=None, volumes:tuple[float, float]=(1.0, 1.0)):
        self.stop()
        self.player_thread_name = create_Thread(target=(self.play_thread), args=(loops, fade_ms, fadeout_ms, add_fade_time, add_fadeout_time, position, volumes))

    def play_thread(self, loops:int=-1, fade_ms:int=0, fadeout_ms:int=0, add_fade_time:bool=False, add_fadeout_time:bool=False, position:float=None, volumes:tuple[float, float]=(1.0, 1.0)):
        '''Don't directly run Music_Player.play_thread(). Run Music_Player.play() instead.'''
        while True:
            for sound in self.playlist:
                sound = SOUNDS[sound] if isinstance(sound, str) else sound
                duration = play_sound(sound, self.channel_name, fade_ms=fade_ms, position=position, volumes=volumes)
                duration += fade_ms if add_fade_time else 0
                duration += fadeout_ms if add_fadeout_time else 0
                st = time.time()
                while time.time() - st < duration:
                    if THREAD_KILLERS[self.player_thread_name]:
                        stop_sound_channel(self.channel_name, fadeout_ms)
                        THREAD_KILLERS.pop(self.player_thread_name)
                        self.player_thread_name = None
                        return
            if loops == 0:
                break
            elif loops != -1:
                loops -= 1

    def stop(self):
        if self.player_thread_name is not None:
            THREAD_KILLERS[self.player_thread_name] = True
    
    def delete(self):
        self.stop()
        MUSIC_PLAYERS.pop(self.name)

MUSIC_PLAYERS:dict[str, Music_Player] = {}
def create_music_player(name:str, playlist:list[str|pg.Sound], channel_name:str="default"):
    MUSIC_PLAYERS[name] = Music_Player(name, playlist, channel_name)

def delete_music_player(name:str="default"):
    MUSIC_PLAYERS[name].delete()

def stop_music_player(name:str="default"):
    MUSIC_PLAYERS[name].stop()

def play_music_player(name:str="default", loops:int=0, fade_ms:int=0, fadeout_ms:int=0, add_fade_time:bool=False, add_fadeout_time:bool=False, position:float=None, volumes:tuple[float, float]=(1.0, 1.0)):
    if RUN_BY_ENGINE:
        return
    MUSIC_PLAYERS[name].play(loops, fade_ms, fadeout_ms, add_fade_time, add_fadeout_time, position, volumes)

SOUND_CHANNELS:dict[str, Sound_Channel] = {"default": Sound_Channel("default")}
def create_sound_channel(name:str="default"):
    SOUND_CHANNELS[name] = Sound_Channel(name)

def delete_sound_channel(name:str="default"):
    SOUND_CHANNELS[name].delete()

def stop_sound_channel(name:str="default", fadeout_ms:int=0):
    SOUND_CHANNELS[name].channel.fadeout(fadeout_ms)

def un_pause_sound_channel(name:str="default", pause:bool=True):
    if pause:
        SOUND_CHANNELS[name].channel.pause()
    else:
        SOUND_CHANNELS[name].channel.unpause()

def revolume_sound_channel(name:str="default", volume:float=1.0):
    SOUND_CHANNELS[name].channel.set_volume(volume)
    SOUND_CHANNELS[name].volume = volume

def un_mute_sound_channel(name:str="default", mute:bool=True):
    SOUND_CHANNELS[name].channel.set_volume(0 if mute else SOUND_CHANNELS[name].volume)

def get_channel_business(name:str="default") -> bool:
    return SOUND_CHANNELS[name].channel.get_busy()

def sound_position_to_lr_volume(position:float):
    return max(0, 1 - position), max(0, position)

def fetch_sound(sound:pg.Sound|str):
    fetched_sound = SOUNDS[sound] if isinstance(sound, str) else sound
    sound_name = sound if isinstance(sound, str) else None
    return fetched_sound, sound_name

def revolume_sound(sound:pg.Sound|str, left_volume:float=None, right_volume:float=None, volume:float=None, overwrite:bool=False):
    overwrite &= isinstance(sound, str)
    sound, sound_name = fetch_sound(sound)
    arr = pg.sndarray.array(sound)
    if volume is not None:
        left_volume, right_volume = volume, volume
    left_channel = arr[:, 0] * left_volume  # Left channel
    right_channel = arr[:, 1] * right_volume  # Right channel
    
    revolumed_sound = pg.sndarray.make_sound(np.int32(np.column_stack((left_channel, right_channel))))
    if overwrite:
        SOUNDS[sound_name] = revolumed_sound
    return revolumed_sound

def stereoize_sound(sound:pg.Sound|str, position:float=None, left_volume:float=None, right_volume:float=None, overwrite:bool=False) -> pg.Sound:
    sound, sound_name = fetch_sound(sound)
    if position is not None:
        left_volume = max(0, 1 - position)
        right_volume = max(0, position)

    if overwrite:
        SOUNDS[sound_name] = revolume_sound(sound, left_volume, right_volume)
    return revolume_sound(sound, left_volume, right_volume)

def pitch_sound(sound:pg.Sound|str, pitch:float=1.0, overwrite:bool=False):
    sound, sound_name = fetch_sound(sound)
    arr = pg.sndarray.array(sound)

    length = int(len(arr) / pitch)
    indices = np.round(np.linspace(0, len(arr) - 1, length)).astype(int)
    indices = np.clip(indices, 0, len(arr) - 1)

    pitched = arr[indices]
    pitched_sound = pg.sndarray.make_sound(pitched)

    # Length in seconds = samples / sample_rate
    sample_rate = pg.mixer.get_init()[0]
    duration = len(pitched) / sample_rate

    if overwrite:
        SOUNDS[sound_name] = pitched_sound
    return pitched_sound, duration

def position_volumes(pos:vec2, screen_size:vec2, max_distance:float=None, min_volume:float=0.0, max_volume:float=1.0) -> tuple[float, float]:
    dpos = pos - (screen_size / 2)
    distance = length(dpos)

    panning = max(0, min(1, dpos.x / (screen_size.x) + 0.5))
    
    max_distance = length(screen_size/2) if max_distance is None else max_distance
    attenuation = min_volume + (1 - min(1, distance / max_distance)) * (max_volume - min_volume)  # Basic attenuation formula
    
    left_volume = max(0, 1 - panning) * attenuation
    right_volume = max(0, panning) * attenuation

    left_volume = min(1, max(0, left_volume))
    right_volume = min(1, max(0, right_volume))

    return left_volume, right_volume

SOUNDS:dict[str, pg.Sound] = {}
def create_sound(sound_name:str, file_name:str="", sound:pg.Sound=None):
    if RUN_BY_PROJECT:
        SOUNDS[sound_name] = pg.Sound("Assets\\" + file_name) if sound is None else sound
    else:
        SOUNDS[sound_name] = pg.Sound(f'Projects\\{get_global("<Project_Opened>").value}\\Assets\\' + file_name) if sound is None else sound
    return SOUNDS[sound_name]

def play_sound(sound:pg.Sound|str, channel_name:str="default", loops:int=0, fade_ms:int=0, pitch:float=1.0, position:float=None, volumes:tuple[float, float]=(1.0, 1.0)):
    if RUN_BY_ENGINE:
        return
    sound = SOUNDS[sound] if isinstance(sound, str) else sound
    duration = SOUND_CHANNELS[channel_name].play(sound, loops, fade_ms, pitch, position, volumes)
    return duration

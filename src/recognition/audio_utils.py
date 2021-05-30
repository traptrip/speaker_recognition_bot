import torch
import torchaudio
import librosa
from speechbrain.lobes.features import Fbank, MFCC


def _get_sample(path, resample=None):
    effects = [
        ["remix", "1"]
    ]
    if resample:
        effects.append(["rate", f'{resample}'])
    return torchaudio.sox_effects.apply_effects_file(path, effects=effects)


def get_speech_sample(audio_path, resample=16000):
    return _get_sample(audio_path, resample=resample)


def crop_audio(waveform, sample_rate, secs=5):
    return waveform[..., :int(secs * sample_rate)]


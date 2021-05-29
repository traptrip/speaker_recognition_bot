import torchaudio


def _get_sample(path, resample=None):
    effects = [
        ["remix", "1"]
    ]
    if resample:
        effects.append(["rate", f'{resample}'])
    return torchaudio.sox_effects.apply_effects_file(path, effects=effects)


def get_speech_sample(audio_path, resample=None):
    return _get_sample(audio_path, resample=resample)


def crop_audio(waveform, sample_rate, secs=5):
    return waveform[..., :int(secs * sample_rate)]


def get_mfcc(waveform, sample_rate):
    mfcc_transform = torchaudio.transforms.MFCC(
        sample_rate=sample_rate,
        n_mfcc=80, melkwargs={'n_fft': 400,
                              'n_mels': 80,
                              'win_length': 25,
                              'hop_length': 10})
    mfcc = mfcc_transform(waveform)
    return mfcc

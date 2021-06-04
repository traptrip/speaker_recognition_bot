import torchaudio
import matplotlib.pyplot as plt
import librosa


def _get_sample(path, resample=None):
    effects = [
        ["remix", "1"]
    ]
    if resample:
        effects.append(["rate", f'{resample}'])
    try:
        wav = torchaudio.sox_effects.apply_effects_file(path, effects=effects)
    except Exception:
        wav = torchaudio.sox_effects.apply_effects_file(path, effects=effects, format='mp3')

    return wav


def get_speech_sample(audio_path, resample=16000):
    return _get_sample(audio_path, resample=resample)


def crop_audio(waveform, sample_rate, secs=5):
    return waveform[..., :int(secs * sample_rate)]


def plot_spectrogram(spec, title=None, ylabel='freq_bin', aspect='auto', xmax=None, power=True):
    fig, axs = plt.subplots(1, 1)
    axs.set_title(title or 'Spectrogram (db)')
    axs.set_ylabel(ylabel)
    axs.set_xlabel('frame')
    if power:
        im = axs.imshow(librosa.power_to_db(spec), origin='lower', aspect=aspect)
    else:
        im = axs.imshow(spec, origin='lower', aspect=aspect)
    if xmax:
        axs.set_xlim((0, xmax))
    fig.colorbar(im, ax=axs)
    plt.show(block=False)

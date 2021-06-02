from pathlib import Path

import torch
import librosa
from torchaudio.transforms import MelSpectrogram
from speechbrain.lobes.models.ECAPA_TDNN import ECAPA_TDNN

from src.recognition.audio_utils import get_speech_sample


class SpeakerRecognizer:
    def __init__(self, app, config):
        self.config = config
        self.storage_manager = app.storage_manager
        self.device = self.config['device']
        self.identification_model = ECAPA_TDNN(
            self.config['input_size'],
            device=self.device,
            lin_neurons=self.config['lin_neurons'],
            activation=torch.nn.ReLU,
            channels=self.config['channels'],
            kernel_sizes=self.config['kernel_sizes'],
            dilations=self.config['dilations'],
            attention_channels=self.config['attention_channels'],
            res2net_scale=self.config['res2net_scale'],
            se_channels=self.config['se_channels']
        )
        # load model weights
        self.identification_model.load_state_dict(torch.load(
            Path(__file__).parent / self.config['weights_path'],
            map_location=torch.device(self.device)))
        self.identification_model.eval()
        # self.compute_features = Fbank(n_mels=80)
        self.compute_features = MelSpectrogram(
                                    sample_rate=self.config['sample_rate'],
                                    n_fft=400,
                                    win_length=int((self.config['sample_rate'] / 1000.0) * 25),
                                    hop_length=int((self.config['sample_rate'] / 1000.0) * 10),
                                    center=True,
                                    pad_mode="constant",
                                    power=2.,
                                    onesided=True,
                                    n_mels=self.config['n_mels'],
                                    window_fn=torch.hamming_window
                                )
        self.cos_sim = torch.nn.CosineSimilarity(dim=1)

    def _preprocess_audio_sample(self, audio_sample):
        waveform, sample_rate = audio_sample
        if len(waveform.shape) == 1:
            waveform = waveform.unsqueeze(0)
        wav_lens = torch.ones(waveform.shape[0])
        waveform, wav_lens = waveform.to(self.device), wav_lens.to(self.device)
        # Computing features
        # features = self.compute_fbank(waveform)
        melspec = self.compute_features(waveform)
        melspec = torch.from_numpy(librosa.power_to_db(melspec))  # get dB MelSpectrogram
        features = melspec.transpose(1, 2)

        return features, wav_lens

    def get_speaker_vector(self, audio_file) -> torch.tensor:
        audio_sample = get_speech_sample(audio_file)
        input_features, wav_lens = self._preprocess_audio_sample(audio_sample)
        speaker_vector = self.identification_model(input_features, wav_lens)

        return speaker_vector[0]

    def get_speaker_info(self, speaker_vector):
        speaker_info = [[], []]
        with torch.no_grad():
            all_speakers = self.storage_manager.get_all_speakers()
            all_vectors = torch.stack([i[2] for i in all_speakers])
            similarities = self.cos_sim(speaker_vector, all_vectors)
            max_similar_idx = similarities.argmax()
            if similarities[max_similar_idx] > self.config['threshold']:
                # id, name, confidence
                speaker_info[0] = all_speakers[max_similar_idx][:-1] + [similarities[max_similar_idx].item()]
            speaker_info[1] = all_speakers[max_similar_idx][:-1] + [similarities[max_similar_idx].item()]
        return speaker_info

    def recognize_speaker(self, audio_file):
        speaker_vector = self.get_speaker_vector(audio_file)
        speaker_info = self.get_speaker_info(speaker_vector)

        return speaker_info


# if __name__ == '__main__':
#     import yaml
#     with open(Path(__file__).parent / "../../config.yml", "r") as yml_file:
#         cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
#
#     sr = SpeakerRecognizer(cfg['recognizer'])
#     vector = sr.get_speaker_vector('./../../data/audios/gob_AgADBA8AAuxvmEk.wav')

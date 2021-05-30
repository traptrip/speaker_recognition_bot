from pathlib import Path

import torch
from speechbrain.lobes.models.ECAPA_TDNN import ECAPA_TDNN
from speechbrain.processing.features import InputNormalization
from speechbrain.lobes.features import Fbank

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
        self.mean_var_norm = InputNormalization(norm_type='sentence', std_norm=False)
        self.compute_features = Fbank(n_mels=80)
        self.cos_sim = torch.nn.CosineSimilarity(dim=1)

    def _preprocess_audio_sample(self, audio_file):
        waveform, sample_rate = get_speech_sample(audio_file)
        if len(waveform.shape) == 1:
            waveform = waveform.unsqueeze(0)
        wav_lens = torch.ones(waveform.shape[0])
        waveform, wav_lens = waveform.to(self.device), wav_lens.to(self.device)
        # Computing features
        features = self.compute_features(waveform)
        features = self.mean_var_norm(features, wav_lens)

        return features, wav_lens

    def get_speaker_vector(self, audio_file) -> torch.tensor:
        input_features, wav_lens = self._preprocess_audio_sample(audio_file)
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









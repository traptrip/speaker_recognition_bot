import pickle
from pathlib import Path
from peewee import Model, CharField, BlobField, IntegerField, SqliteDatabase


db = SqliteDatabase(Path(__file__).parent / '../data/speakers.db')


class Speaker(Model):
    speaker_id = IntegerField(primary_key=True)
    name = CharField(max_length=255)
    vector = BlobField()

    class Meta:
        database = db


class StorageManager:
    def __init__(self):
        Speaker.create_table()

    @classmethod
    def add_speaker(cls, speaker_name, speaker_vector):
        speaker_vector_dump = pickle.dumps(speaker_vector)
        Speaker.create(name=speaker_name,
                       vector=speaker_vector_dump)

    @classmethod
    def get_all_speakers(cls):
        all_speakers_query = Speaker.select()
        speakers = [[s.speaker_id, s.name, pickle.loads(s.vector)] for s in all_speakers_query]
        return speakers


if __name__ == '__main__':
    sm = StorageManager()
    sm.get_all_speakers()

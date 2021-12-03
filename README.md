# speaker_recognition_bot

## Before you start 
- add your telegram bot token in **config.yml** (see example_config.yml)
- add your pretrained weights for ecapa-tdnn model in **./src/recognition/weights** (my pretrained weights: https://disk.yandex.com/d/qa2cUQUxMSBMWw)

## Start app with Docker
```bash
docker build -f Dockerfile -t speaker_rec_bot .  
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/config.yml:/app/config.yml" \
  -v "$(pwd)/src/recognition/weights:/app/src/recognition/weights" \
  --name speaker_bot -d speaker_rec_bot
```

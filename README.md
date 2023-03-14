# telegram_bot_opsec
A basic opsec bot for Telegram used for quickly looking up usernames & accounts. Based off WhatsMyName Framework ([Website](https://whatsmyname.app/), [GitHub](https://github.com/webbreacher/whatsmyname)).

Note that a majority of python 3 libraries in requirements.txt are required by the whatsmyname framework, and as such are installed on docker image build in order to run it. This, unfortunately, results in a larger docker image size than is ideal. At a later date, I will fork the WMN repo and create a 'lite' version that contains exclusively our lookup requirement & build into an Alpine image.

### Building and Running.
- Build with: `docker build -t opsec-bot .`
- Run with: `docker run opsec-bot -a yourapikeyhere`

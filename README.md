# OnionTalks
A little Streamlit-app using Whisper with which one can transcribe spoken audio into written words. 

## About The Project
This is a small app I assembled in Python for fun to transcribe tabletop RPG-sessions. It uses OpenAI's Whisper to do so. The app is very simple and runs entirely locally. It simply records spoken audio and, once the recording is done, it feeds the recording to a selected Whisper model and then processes its output. 

The app automatically downloads the model you selected (there's three options) on your machine's local storage if it cannot find them. Note that this does mean the app requires some free storage space. Once those are downloaded, the app can run without access to the internet. You download them by simply selecting them in the sidebar of the app's UI. 

The easiest way to create new transcripts if you've already created one is to refresh the page. A 'clear-transcription'-button turned out to be surprisingly hard to make. 

Have fun with it!

## Getting started
Use the following steps:
1. Open a command line terminal
2. Clone this repository
3. Create a fresh Python Environment running on a semi-recent Python-version. I used Python verison 3.11. I like to use [Anaconda](https://www.anaconda.com/): ```conda create --name oniontalks python=3.11```, but venvs or other alternatives should work just as well.
4. Activate it: ```conda activate oniontalks```
5. Run the app: ```streamlit run OnionTalks.py```
6. Have fun! ```python run good_times.p... wait no.```

It is possible to create a local executable .exe-file to run the app on Windows using [pyinstaller](https://pyinstaller.org/en/stable/). run_OnionTalks.py is added as a setup for you to do so. It isn't easy and takes quite a bit of tinkering and trial-and-error, but I have succeeded at doing so at some point. It does so by making OnionTalks.py runnable directly from a ```python run```-command instead of having to use ```streamlit run```.  

## Credits
- [Streamlit](https://streamlit.io/) is a great tool for assembling UI's quickly and easily in Python. It is what was used to create this application.
- [Whisper's OpenAI](https://github.com/openai/whisper) is both the name of the variety of models and the package used to service them to do what the app -well- does: transcribing audio. Huge credits to their easy-to-use library and free access to models. 
# Import libraries
import streamlit
import streamlit.web.cli as stcli
import streamlit.runtime.scriptrunner.magic_funcs
import os, sys 
import io
import numpy as np
import whisper
import torch
import tempfile
import os
import collections

# Check if this script is being run as the main program
if __name__ == "__main__":
    # Change directory to the current script's location
    os.chdir(os.path.dirname(__file__))
    
    # Set up command-line arguments for Streamlit
    sys.argv = [
        # Specify Streamlit command to run the app
        "streamlit",
        # Specify the Python file containing the app code
        "run",
        # Specify the app filename
        "OnionTalks.py",
        # Configure server settings
        "--server.port=1337",     # Tweak the upload size to a choice of yours (1024MB = 1GB), default is 200MB
        "--global.developmentMode=false",
        # Set theme colors
        "--theme.primaryColor=#32CD32",
    ]
    
    # Run Streamlit CLI
    stcli.main()
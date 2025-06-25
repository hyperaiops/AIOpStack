import os
import sys
from streamlit.web import cli as stcli

def main():
    # Get directory where cli.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")

    # Ensure working directory is the same as the script's folder
    os.chdir(script_dir)

    # Run app.py if no additional args
    if len(sys.argv) == 1:
        sys.argv = ["streamlit", "run", app_path]
    else:
        # Prepend "streamlit" to allow full CLI passthrough
        sys.argv = ["streamlit"] + sys.argv[1:]

    sys.exit(stcli.main())
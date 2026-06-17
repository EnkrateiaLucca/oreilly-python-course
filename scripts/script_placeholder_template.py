# REPLAXE THE BRACKETS!! []

# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
[Replace with a description like: "This is whsat the script does..."]

[Replace with how to run the script like uv run .....py]
"""

# import statements
import argparse
#....the other imports

# Add the functions and processing here

def main():
    """Parse the command line and route to either the CLI or the server."""
    parser = argparse.ArgumentParser(description="What the tool does")
    
    # you can add commands
    # sub = parser.add_subparsers(dest="command", required=True)

    # `query` subcommand: one positional arg + an optional sentence cap.
    parser.add_argument("--input", default="input")
    
    args = parser.parse_args()
    
    

if __name__=="__main__":
    main()



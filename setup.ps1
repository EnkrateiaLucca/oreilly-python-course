git clone https://github.com/EnkrateiaLucca/oreilly-python-course
cd oreilly-python-course
uv sync
uv run ipython kernel install --user --env VIRTUAL_ENV "$PWD\.venv" --name=oreilly-automate-py
playwright install
Write-Output "✅ Setup complete! To execute the jupyter environment for the interactive notebooks run:"
uv run --with jupyter jupyter lab

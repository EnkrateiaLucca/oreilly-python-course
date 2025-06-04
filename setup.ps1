# Set project name (adjust as needed)
$projectName = "my-uv-project"
$kernelDisplayName = "My UV Project"

Write-Output "🔧 Initializing project..."
uv init --bare

Write-Output "📦 Installing JupyterLab and ipykernel..."
uv add --dev jupyterlab ipykernel

Write-Output "🧠 Registering Jupyter kernel..."
uv run python -m ipykernel install --user --name=$projectName --display-name "$kernelDisplayName"

Write-Output "✅ Setup complete. Run with:"
Write-Output "uv run jupyter lab"

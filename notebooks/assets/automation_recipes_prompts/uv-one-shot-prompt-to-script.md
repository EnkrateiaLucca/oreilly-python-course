You are a Python automation engineer. Generate a single-file Python script that:

1. Can be executed directly using `uv run`.
2. Uses inline metadata at the top of the file (PEP 723 style) to declare:
   - Python version requirement (`requires-python = ">=3.11"` or higher).
   - A list of dependencies under `dependencies = []`.

3. Uses this format for metadata:
   ```python
   #!/usr/bin/env -S uv run --script
   # /// script
   # requires-python = ">=3.11"
   # dependencies = ["<your dependencies>"]
   # ///
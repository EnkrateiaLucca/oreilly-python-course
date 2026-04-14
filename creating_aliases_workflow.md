## Mac Workflow (your current approach)

1. **Python script** lives at a path (e.g., `~/scripts/my_script.py`)
2. **Command to run**: `uv run ~/scripts/my_script.py`
3. **Accept arguments**: `uv run ~/scripts/my_script.py "$@"` passes all args
4. **Create alias** in `~/.aliases`:
   ```bash
   alias myscript='uv run ~/scripts/my_script.py'
   ```
   Or as a function for arguments:
   ```bash
   myscript() { uv run ~/scripts/my_script.py "$@"; }
   ```
5. **Source it** from `.zshrc` or `.bashrc`: `source ~/.aliases`

---

## Windows Equivalent

1. **Python script** lives at a path (e.g., `C:\scripts\my_script.py`)

2. **Command to run**: `uv run C:\scripts\my_script.py`

3. **Create a PowerShell function** in your profile:
   - Open/create your profile: `notepad $PROFILE`
   - Add a function:
     ```powershell
     function myscript { uv run C:\scripts\my_script.py @args }
     ```
   - `@args` passes all arguments through (equivalent to `"$@"`)

4. **Reload profile**: `. $PROFILE` or restart terminal

5. **(Optional) Organize aliases**: Create a separate file like `C:\Users\<you>\aliases.ps1`, then source it from `$PROFILE`:
   ```powershell
   . "$HOME\aliases.ps1"
   ```

---

**Alternative (batch files)**: Create `myscript.cmd` in a folder that's in your PATH:
```cmd
@echo off
uv run C:\scripts\my_script.py %*
```
`%*` passes all arguments.
# Windows Setup Guide - Complete Beginner's Edition

This guide will walk you through setting up the O'Reilly Python course on Windows, step-by-step. Don't worry if you're new to this - we'll cover everything!

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1: Install Python](#step-1-install-python)
- [Step 2: Install Git](#step-2-install-git)
- [Step 3: Install UV Package Manager](#step-3-install-uv-package-manager)
- [Step 4: Clone and Setup Project](#step-4-clone-and-setup-project)
- [Step 5: Install Playwright Browsers](#step-5-install-playwright-browsers)
- [Step 6: Setup API Keys](#step-6-setup-api-keys)
- [Step 7: Launch Jupyter Lab](#step-7-launch-jupyter-lab)
- [Common Issues & Solutions](#common-issues--solutions)

---

## Prerequisites

### What You'll Need
- A Windows 10 or Windows 11 computer
- Administrator access to your computer
- An internet connection
- About 30 minutes of time

### Important Notes Before Starting
- **Antivirus/Firewall**: You may need to temporarily allow installations or add exceptions for Python, UV, and Git
- **Windows Defender**: May flag installers as unknown - this is normal for development tools
- **Execution Policy**: Some commands require changing PowerShell execution policy (we'll cover this)

---

## Step 1: Install Python

### 1.1 Check If Python Is Already Installed

1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. In the black window that appears, type:
   ```cmd
   python --version
   ```
4. If you see `Python 3.13.x` or higher, **skip to Step 2**
5. If you see an error or a version lower than 3.13, continue below

### 1.2 Download Python 3.13

1. Go to: https://www.python.org/downloads/
2. Click the yellow "Download Python 3.13.x" button
3. **Important**: When the installer runs:
   - ✅ **CHECK** the box that says "Add Python to PATH" (at the bottom)
   - Click "Install Now"
   - If asked for Administrator permission, click "Yes"

### 1.3 Verify Python Installation

1. **Close any open Command Prompt/PowerShell windows** (this is important!)
2. Press `Windows Key + R`
3. Type `cmd` and press Enter
4. Type:
   ```cmd
   python --version
   ```
5. You should see: `Python 3.13.x`

**✅ Checkpoint**: If you see the Python version, you're ready for Step 2!

**❌ Troubleshooting**: If it says "Python is not recognized":
- Make sure you closed all old terminal windows
- Restart your computer
- If still not working, see [Common Issues](#python-not-found-error)

---

## Step 2: Install Git

### 2.1 Check If Git Is Already Installed

1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. Type:
   ```cmd
   git --version
   ```
4. If you see `git version x.x.x`, **skip to Step 3**
5. If you see an error, continue below

### 2.2 Download Git

1. Go to: https://git-scm.com/download/win
2. The download should start automatically
3. Run the installer (Git-2.x.x-64-bit.exe)

### 2.3 Git Installation Settings

**Most users can just click "Next" through all options.** Here are the key screens:

1. **Select Components**: Keep defaults ✅
2. **Default Editor**: Choose "Use Notepad" (or your preferred editor)
3. **PATH Environment**: Choose "Git from the command line and also from 3rd-party software" ✅
4. **Line Ending**: Choose "Checkout Windows-style, commit Unix-style" ✅
5. **Terminal Emulator**: Choose "Use Windows' default console window" ✅
6. Continue clicking "Next" and then "Install"

### 2.4 Verify Git Installation

1. **Close any open Command Prompt/PowerShell windows**
2. Press `Windows Key + R`
3. Type `cmd` and press Enter
4. Type:
   ```cmd
   git --version
   ```
5. You should see: `git version x.x.x`

**✅ Checkpoint**: If you see the Git version, you're ready for Step 3!

---

## Step 3: Install UV Package Manager

This is where students commonly face issues. Let's go through it carefully.

### 3.1 Open PowerShell as Administrator

**Method 1** (Recommended):
1. Press `Windows Key`
2. Type `PowerShell`
3. Right-click on "Windows PowerShell"
4. Click "Run as administrator"
5. Click "Yes" if asked for permission

**Method 2**:
1. Press `Windows Key + X`
2. Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

### 3.2 Allow Script Execution (May be required)

If you get an error about execution policy later, run this command first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

When asked "Do you want to change the execution policy?", type `Y` and press Enter.

**What this does**: Allows you to run downloaded PowerShell scripts (required for UV installation)

### 3.3 Install UV

In the same PowerShell window (still as Administrator), run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**What to expect**:
- You'll see text downloading and installing UV
- Takes about 30 seconds to 2 minutes
- You should see a message about UV being installed successfully

### 3.4 Handle Firewall/Antivirus Warnings

**Windows Defender SmartScreen**:
- If you see "Windows protected your PC":
  - Click "More info"
  - Click "Run anyway"

**Antivirus Software**:
- If your antivirus blocks the download:
  - Temporarily disable it, OR
  - Add an exception for the UV installer
  - You can re-enable it after installation

### 3.5 Restart PowerShell

**Important**: Close the PowerShell window and open a new one (you can use regular PowerShell now, doesn't need to be Admin)

### 3.6 Verify UV Installation

In a **new** PowerShell window:

```powershell
uv --version
```

You should see: `uv x.x.x`

**✅ Checkpoint**: If you see the UV version, you're ready for Step 4!

**❌ Troubleshooting**: If it says "uv is not recognized":
- See [UV Not Found Error](#uv-not-found-error) in Common Issues
- May need to add UV to PATH manually (covered in troubleshooting)

---

## Step 4: Clone and Setup Project

### 4.1 Choose Your Project Location

1. Open File Explorer
2. Navigate to where you want the course folder (e.g., `C:\Users\YourName\Documents\`)
3. Right-click in the folder → "Open in Terminal" or "Open PowerShell window here"
   - If you don't see this option: Hold Shift, then right-click → "Open PowerShell window here"

### 4.2 Clone the Repository

In the PowerShell window at your chosen location:

```powershell
git clone https://github.com/EnkrateiaLucca/oreilly-python-course
```

**What to expect**:
- You'll see: "Cloning into 'oreilly-python-course'..."
- Progress bars showing the download
- Takes about 1-3 minutes depending on internet speed

### 4.3 Navigate to Project Folder

```powershell
cd oreilly-python-course
```

### 4.4 Sync Dependencies with UV

**This is the main setup step - it will take several minutes:**

```powershell
uv sync
```

**What to expect**:
- UV will create a virtual environment (.venv folder)
- Download and install all Python packages (50+ packages!)
- Takes 3-10 minutes depending on internet speed
- You'll see lots of "Downloading..." and "Installing..." messages

**⚠️ Common Issues During Sync**:

**If you see "Failed to download" errors**:
- Check your internet connection
- If behind a corporate firewall, you may need to configure proxy settings
- Try again - sometimes downloads fail temporarily

**If you see "Permission denied" errors**:
- Your antivirus might be blocking file creation
- Try temporarily disabling antivirus
- Or add the `oreilly-python-course` folder to antivirus exceptions

**If UV seems stuck**:
- Wait 5-10 minutes - large packages like numpy/pandas take time
- You should see progress messages periodically
- If truly frozen (no messages for 10+ minutes), press `Ctrl + C` and try again

### 4.5 Install Jupyter Kernel

This creates a custom Python kernel for the notebooks:

```powershell
uv run ipython kernel install --user --env VIRTUAL_ENV "$PWD\.venv" --name=oreilly-automate-py
```

**What to expect**:
- You'll see: "Installed kernelspec oreilly-automate-py in..."
- This registers the environment with Jupyter

**✅ Checkpoint**: If you see the "Installed kernelspec" message, continue to Step 5!

---

## Step 5: Install Playwright Browsers

Playwright is used for browser automation. It needs to download browser binaries.

### 5.1 Install Browsers

```powershell
uv run playwright install
```

**What to expect**:
- Downloads Chromium, Firefox, and WebKit browsers
- Takes 2-5 minutes
- Downloads about 400-500 MB

**⚠️ If you see "Access denied" or permission errors**:
- Run PowerShell as Administrator for this step
- Or add exception in antivirus

**⚠️ If download fails**:
- Check internet connection
- Check firewall settings
- Try running: `uv run playwright install chromium` (just Chrome browser)

**✅ Checkpoint**: Setup is almost complete! Just need API keys and you're ready.

---

## Step 6: Setup API Keys

The course uses OpenAI and Anthropic AI services. You'll need API keys.

### 6.1 Get API Keys

**OpenAI**:
1. Go to: https://platform.openai.com/
2. Sign up or log in
3. Click on your profile → "View API keys"
4. Click "Create new secret key"
5. **Copy the key immediately** (you won't see it again!)

**Anthropic (Claude)**:
1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Go to "API Keys"
4. Click "Create Key"
5. **Copy the key immediately**

### 6.2 Create .env File

1. In the `oreilly-python-course` folder, find the file `.env.example`
2. **Make a copy** of this file and rename it to `.env` (no .example)
   - **Note**: It's just `.env` - no name before the dot
3. Open `.env` in Notepad or any text editor
4. Replace the placeholder text with your actual keys:

```
OPENAI_API_KEY=your-actual-openai-key-here
ANTHROPIC_API_KEY=your-actual-anthropic-key-here
```

5. Save and close the file

**⚠️ Important**:
- Never share your .env file
- Never commit it to git (it's already in .gitignore)
- Keep your API keys secret

---

## Step 7: Launch Jupyter Lab

You're ready to start the course!

### 7.1 Start Jupyter Lab

From the PowerShell window in your `oreilly-python-course` folder:

```powershell
uv run --with jupyter jupyter lab
```

**What to expect**:
- You'll see several startup messages
- Your default web browser will open automatically
- You'll see the Jupyter Lab interface with all course notebooks

### 7.2 Verify Everything Works

In Jupyter Lab:
1. Navigate to `notebooks/01-python-fundamentals/`
2. Open `01-python-basics.ipynb`
3. In the top-right, verify the kernel says "oreilly-automate-py"
4. Run the first cell (Shift + Enter)

**✅ Success!** If the cell runs without errors, you're all set up!

---

## Common Issues & Solutions

### Python Not Found Error

**Symptom**: `'python' is not recognized as an internal or external command`

**Solutions**:
1. Close all terminal windows and try again
2. Restart your computer
3. Manually add Python to PATH:
   - Press `Windows Key + R`
   - Type `sysdm.cpl` and press Enter
   - Click "Environment Variables"
   - Under "User variables", find "Path", click "Edit"
   - Click "New" and add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\`
   - Click "New" again and add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\Scripts\`
   - Click OK on all windows
   - Restart terminal

### UV Not Found Error

**Symptom**: `'uv' is not recognized as an internal or external command`

**Solutions**:
1. Close and reopen PowerShell (UV requires a fresh terminal)
2. Check if UV actually installed:
   - Look for: `C:\Users\YourUsername\.cargo\bin\uv.exe`
3. If UV exists but not recognized, add to PATH:
   - Press `Windows Key + R`
   - Type `sysdm.cpl` and press Enter
   - Click "Environment Variables"
   - Under "User variables", find "Path", click "Edit"
   - Click "New" and add: `C:\Users\YourUsername\.cargo\bin\`
   - Click OK, restart terminal
4. If UV doesn't exist at all, try alternative installation:
   ```powershell
   # Using winget (Windows 11)
   winget install --id=astral-sh.uv -e
   ```

### Firewall Blocking Downloads

**Symptom**: Downloads fail, "Connection timed out", "Access denied"

**Solutions**:
1. **Windows Defender Firewall**:
   - Press `Windows Key`
   - Type "Firewall"
   - Click "Windows Defender Firewall"
   - Click "Allow an app through firewall"
   - Find Python, UV, and Git - make sure both Private and Public are checked
   - If not listed, click "Allow another app" and browse to add them

2. **Corporate/School Firewall**:
   - May need to use a personal network
   - Or contact IT to allow astral.sh, github.com, python.org

3. **Antivirus Software** (Norton, McAfee, Avast, etc.):
   - Temporarily disable during installation
   - Or add exceptions for:
     - `C:\Users\YourUsername\.cargo\`
     - Your project folder
     - Python installation folder

### Execution Policy Error

**Symptom**: "cannot be loaded because running scripts is disabled on this system"

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Type `Y` when asked to confirm.

### UV Sync Taking Forever

**Symptom**: `uv sync` seems frozen

**Solutions**:
1. Wait patiently - large packages take time (numpy, pandas can be 50+ MB each)
2. Check if progress messages are appearing every minute or so
3. If truly frozen (10+ minutes with no output):
   - Press `Ctrl + C`
   - Delete the `.venv` folder
   - Run `uv sync` again
4. Try verbose mode to see what's happening:
   ```powershell
   uv sync -v
   ```

### Jupyter Lab Won't Open

**Symptom**: Browser doesn't open, or shows "Connection refused"

**Solutions**:
1. Check if the terminal shows errors
2. Try a different browser
3. Manually open browser and go to the URL shown in terminal (usually http://localhost:8888)
4. Check if another Jupyter instance is running:
   ```powershell
   # Stop all Jupyter processes
   taskkill /f /im jupyter-lab.exe
   # Try again
   uv run --with jupyter jupyter lab
   ```

### Wrong Kernel in Jupyter

**Symptom**: Notebooks use wrong Python kernel

**Solutions**:
1. In Jupyter Lab, click the kernel name (top-right)
2. Click "Change kernel"
3. Select "oreilly-automate-py"
4. If not listed, go back to Step 4.5 and reinstall the kernel

### Import Errors in Notebooks

**Symptom**: `ModuleNotFoundError: No module named 'anthropic'` (or other modules)

**Solutions**:
1. Make sure you're using the "oreilly-automate-py" kernel
2. Verify `uv sync` completed successfully
3. Try reinstalling dependencies:
   ```powershell
   uv sync --reinstall
   ```

---

## Need More Help?

1. **Course Issues**: Open an issue at https://github.com/EnkrateiaLucca/oreilly-python-course/issues
2. **UV Issues**: Check UV docs at https://docs.astral.sh/uv/
3. **Python Issues**: Check Python docs at https://docs.python.org/3/

---

## Quick Reference

**Start working on the course**:
```powershell
cd path\to\oreilly-python-course
uv run --with jupyter jupyter lab
```

**Update dependencies**:
```powershell
uv sync
```

**Reinstall everything**:
```powershell
# Delete .venv folder first
uv sync
uv run ipython kernel install --user --env VIRTUAL_ENV "$PWD\.venv" --name=oreilly-automate-py
uv run playwright install
```

---

**🎉 Congratulations!** You've successfully set up your Python development environment. Time to start learning!

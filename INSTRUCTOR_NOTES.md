# Instructor Notes - Windows Setup Resources

## What's Been Created

I've created a comprehensive Windows setup system for your students to address common issues:

### 1. **WINDOWS_SETUP.md** - Complete Beginner's Guide
   - **Purpose**: Detailed step-by-step instructions for absolute beginners
   - **Length**: ~30 minutes to read and follow
   - **Covers**:
     - Python installation with PATH setup
     - Git installation with proper settings
     - UV installation with firewall/antivirus handling
     - Complete troubleshooting section for every common error
   - **Use when**: Students are setting up for the first time or having issues

### 2. **setup-windows.ps1** - Automated Setup Script
   - **Purpose**: One-click setup that handles most common issues
   - **Features**:
     - Checks prerequisites (Python, Git)
     - Auto-installs UV if missing
     - Provides helpful error messages with solutions
     - Handles all setup steps automatically
   - **Use when**: Students want the easiest path
   - **Run with**: `.\setup-windows.ps1`

### 3. **diagnose-setup.ps1** - Diagnostic Tool
   - **Purpose**: Identifies what's wrong with a broken setup
   - **Checks**:
     - Python version and installation
     - Git availability
     - UV installation and PATH
     - Virtual environment status
     - Network connectivity
     - Firewall issues
   - **Use when**: Students report "it's not working" but you need specifics
   - **Run with**: `.\diagnose-setup.ps1`

### 4. **QUICK_START_WINDOWS.md** - 5-Minute Reference
   - **Purpose**: Quick reference card for experienced users
   - **Length**: Can be skimmed in 1-2 minutes
   - **Use when**: Students just need a command reminder

### 5. **Updated README.md** - Main Entry Point
   - Now prominently points Windows users to these resources
   - Clear distinction between automated and manual setup
   - Links to diagnostic tool

---

## Common Student Issues & Solutions

### Issue 1: "UV not found" (Most Common)
**Why it happens**:
- Students don't restart terminal after UV install
- UV installer didn't add to PATH due to permissions
- Corporate antivirus blocked the installer

**Solutions provided**:
- Setup script checks this and provides clear instructions
- Diagnostic script identifies if UV exists but isn't in PATH
- WINDOWS_SETUP.md has step-by-step PATH addition instructions

### Issue 2: Firewall Blocking Downloads
**Why it happens**:
- Corporate/school networks block Python package downloads
- Windows Defender flags unknown installers
- Antivirus software blocks file creation in project folder

**Solutions provided**:
- Setup script warns about this upfront
- Detailed firewall configuration in WINDOWS_SETUP.md
- Diagnostic script tests connectivity to PyPI, GitHub, etc.

### Issue 3: Wrong Python Version
**Why it happens**:
- Students have Python 2.7 or 3.8 from old installations
- Multiple Python versions creating PATH conflicts
- Python installed but "Add to PATH" wasn't checked

**Solutions provided**:
- Setup script checks version before proceeding
- Clear version check instructions in guide
- Diagnostic script identifies version issues

### Issue 4: PowerShell Execution Policy
**Why it happens**:
- Default Windows security blocks running downloaded scripts
- Students try to run .ps1 files without enabling scripts

**Solutions provided**:
- Setup script uses ByPass for UV installation
- WINDOWS_SETUP.md includes execution policy setup
- Diagnostic script checks current policy

### Issue 5: UV Sync Appears Frozen
**Why it happens**:
- Large packages (numpy, pandas) take time to compile on Windows
- Slow internet makes it seem frozen
- Students don't realize it's normal to take 5-10 minutes

**Solutions provided**:
- Setup script shows progress expectations ("This takes 3-10 minutes...")
- WINDOWS_SETUP.md explains what to expect
- Troubleshooting section on when to actually worry

---

## Recommended Student Flow

### For Beginners (Most Students)
1. **Pre-class**: Email link to WINDOWS_SETUP.md
2. **Start here**: Run `setup-windows.ps1`
3. **If issues**: Check WINDOWS_SETUP.md troubleshooting
4. **Still stuck**: Run `diagnose-setup.ps1` and share output

### For Experienced Users
1. Point to QUICK_START_WINDOWS.md
2. They can use manual commands

### For Problem-Solving During Class
1. Student reports issue
2. Ask them to run: `.\diagnose-setup.ps1`
3. They share the output (screenshot or copy/paste)
4. You immediately see what's wrong (Python version, missing UV, etc.)

---

## Pre-Class Email Template

Subject: Setting Up Your Python Environment - Please Do Before Class

Hi everyone,

Before our O'Reilly Python course, please set up your environment:

**Windows Users (3 options - choose one):**

**Option 1 - Easiest (Recommended):**
1. Install Python 3.13: https://www.python.org/downloads/ (CHECK "Add to PATH"!)
2. Install Git: https://git-scm.com/download/win
3. Clone the repo: `git clone https://github.com/EnkrateiaLucca/oreilly-python-course`
4. Run our setup script: `.\setup-windows.ps1`

**Option 2 - Step-by-step guide:**
Follow WINDOWS_SETUP.md in the repository (great for beginners)

**Option 3 - Quick start:**
See QUICK_START_WINDOWS.md if you're comfortable with command line

**Mac/Linux Users:**
Follow the README.md instructions

**Having problems?**
1. Run `.\diagnose-setup.ps1` to identify issues
2. Check the troubleshooting section in WINDOWS_SETUP.md
3. Email me the output from diagnose-setup.ps1 if still stuck

**To verify it worked:**
Run `uv run --with jupyter jupyter lab` - if Jupyter opens in your browser, you're ready!

See you in class!

---

## During-Class Support Strategy

### If someone has setup issues during class:

**Quick fix attempt (2 minutes):**
```powershell
.\diagnose-setup.ps1
```
This immediately shows what's wrong.

**If it's a quick fix** (UV not in PATH, wrong kernel, etc.):
- Reference the specific section in WINDOWS_SETUP.md
- Or run the setup script: `.\setup-windows.ps1`

**If it's a complex issue** (Python not installed, major firewall issues):
- Suggest they pair with someone who has it working
- Provide cloud environment alternative (Google Colab, etc.)
- Help them fix it during a break

---

## Files Reference

| File | Size | Use Case |
|------|------|----------|
| WINDOWS_SETUP.md | ~15 pages | Complete reference, troubleshooting |
| setup-windows.ps1 | Automated | One-click setup |
| diagnose-setup.ps1 | Diagnostic | Problem identification |
| QUICK_START_WINDOWS.md | 1 page | Quick reference |
| README.md | Updated | Main entry point |

---

## Testing the Scripts

Before distributing to students, test in a Windows VM:

1. **Fresh Windows 10/11 VM** (or test machine)
2. Run `setup-windows.ps1`
3. Verify it handles:
   - Missing Python gracefully
   - UV installation
   - Firewall prompts
4. Test `diagnose-setup.ps1` on:
   - Clean install (should pass all checks)
   - Broken install (remove UV from PATH, etc.)

---

## Maintenance Notes

**Before each course:**
- Update Python version requirements in all docs if needed (currently 3.13+)
- Test setup script on fresh Windows install
- Check if UV installation URL changed

**If pyproject.toml changes:**
- Setup scripts don't need updates (they just run `uv sync`)
- But verify new dependencies don't cause Windows-specific issues

---

## Additional Tips

**Zoom/Screen Sharing:**
- If helping students remotely, ask them to share diagnostic output first
- Much faster than watching them navigate settings

**Common Quick Wins:**
- "Close terminal and open new one" solves 30% of PATH issues
- "Run PowerShell as Admin" solves most permission issues
- "Turn off VPN" sometimes needed for package downloads

**Time Estimates:**
- Clean install with good internet: 10-15 minutes
- With troubleshooting: 20-30 minutes
- With major issues (firewall, no Python): 45+ minutes

**Fallback Options:**
If a student can't get local setup working:
- Google Colab (cloud-based Jupyter)
- Replit (cloud-based Python environment)
- Pair programming with working setup

---

Good luck with your course! These resources should handle 90%+ of Windows setup issues.

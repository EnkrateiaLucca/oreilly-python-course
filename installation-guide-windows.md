## 🖥️ Windows Installation Guide

### **1. Install Git**

1. Download Git from [https://git-scm.com/download/win](https://git-scm.com/download/win).
2. Run the installer (**keep the default settings**).
3. Verify installation:
   ```cmd
   git --version
   ```
   ✅ You should see `git version 2.x.x`.

---

### **2. Install Python 3.11**

1. Download Python from [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. **Check the box** for **"Add Python to PATH"** before installing.
3. Verify installation:
   ```cmd
   python --version
   ```
   ✅ It should print **Python 3.11.x**.

---

### **3. Verify & Upgrade pip (Python's Package Manager)**

1. Ensure pip is installed:
   ```cmd
   python -m ensurepip --default-pip
   ```
2. Upgrade pip:
   ```cmd
   python -m pip install --upgrade pip
   ```
3. Check the pip version:
   ```cmd
   pip --version
   ```
   ✅ If you see `pip 23.x.x`, pip is working fine!

**Note:** You can run these commands in either **Command Prompt (cmd)** or **PowerShell**.

---

## 🎉 You're Ready to Automate Tasks!
Now that you have **Git and Python 3.11 installed**, you can start writing scripts and automating tasks!

Example: To install the `requests` package, run:
```bash
pip install requests
```

Let me know if you need help! 🚀


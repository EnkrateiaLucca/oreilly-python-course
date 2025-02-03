# O'Reilly Live Trainining - Getting Started with LLM Agents using LangChain

## Setup

- [Download Python if you don't have it locally](https://www.python.org/downloads/)
- For this course we will be using: `Python 3.11.11`:

![](./notebooks/assets-resources/python-download.png)

**Conda**

- Install [anaconda](https://www.anaconda.com/download) or [miniconda](https://docs.anaconda.com/miniconda/)
- This repo was tested on a Mac with python=3.11.
- Create an environment: `conda create -n oreilly-automate-tasks python=3.11`
- Activate your environment with: `conda activate oreilly-automate-tasks`
- Install requirements with: `pip install -r requirements/requirements.txt`
- Setup your [Openai API key](https://platform.openai.com/)
- Setup your [Anthropic API key](https://console.anthropic.com/login?returnTo=%2F%3F)
- Download [Ollama](https://ollama.ai/)

**Pip**


1. **Create a Virtual Environment:**
    Navigate to your project directory. Make sure you have python3.11 installed! 
    If using Python 3's built-in `venv`: `python -m venv oreilly-automate-tasks`
    If you're using `virtualenv`: `virtualenv oreilly-automate-tasks`

2. **Activate the Virtual Environment:**
    - **On Windows:**: `.\oreilly-automate-tasks\Scripts\activate`
    - **On macOS and Linux:**: `source oreilly-automate-tasks/bin/activate`

3. **Install Dependencies from `requirements.txt`:**
    ```bash
    pip install python-dotenv
    pip install -r ./requirements/requirements.txt
    ```

4. Setup your openai [API key](https://platform.openai.com/)

Remember to deactivate the virtual environment afterwards: `deactivate`

## Setup your .env file

- Change the `.env.example` file to `.env` and add your OpenAI API key.

```bash
OPENAI_API_KEY=<your openai api key>
ANTHROPIC_API_KEY=<your claude api key>
....
```

## To use this Environment with Jupyter Notebooks:

- ```conda install jupyter -y```
- ```python -m ipykernel install --user --name=oreilly-automate-tasks```

## Notebooks

Here are the notebooks available in the `notebooks/` folder:

1. [Python Basics: Data Types, Strings, Operators (Updated)](notebooks/1.0-python-basics-data-types-strings-operators-updated.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.0-python-basics-data-types-strings-operators-updated.ipynb)

2. [Python Basics: Variables (Updated)](notebooks/1.1-python-basics-variables-updated.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.1-python-basics-variables-updated.ipynb)

3. [Python Basics: Functions (Updated)](notebooks/1.2-python-basics-functions-updated.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.2-python-basics-functions-updated.ipynb)

4. [Python Basics: Lists, For Loops (Updated)](notebooks/1.3-python-basics-lists-for-loops-updated.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.3-python-basics-lists-for-loops-updated.ipynb)

5. [Python Basics: Dictionaries](notebooks/1.4-python-basics-dictionaries.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.4-python-basics-dictionaries.ipynb)

6. [Python Basics: Comparators (Updated)](notebooks/1.5-python-basics-comparators-updated.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.5-python-basics-comparators-updated.ipynb)

7. [Python Basics: Conditionals, Branching Decisions](notebooks/1.6-python-basics-conditionals-branching-decisions.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.6-python-basics-conditionals-branching-decisions.ipynb)

8. [Python Basics: Working with Files](notebooks/1.7-python-basics-working-with-files.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.7-python-basics-working-with-files.ipynb)

9.  [Python Basics: Working with Tabular Data (CSVs)](notebooks/1.8-python-basics-working-with-tabular-data-csvs.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.8-python-basics-working-with-tabular-data-csvs.ipynb)

10.  [Python Basics: Packages and APIs](notebooks/1.9-python-basics-packages-and-apis.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/1.9-python-basics-packages-and-apis.ipynb)

11.  [Building AI Scheduler Agent](notebooks/10.0-building-ai-scheduler-agent.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/10.0-building-ai-scheduler-agent.ipynb)

12.  [Extracting Data from Receipts, Storing CSV](notebooks/11.0-extracting-data-from-receipts-storing-csv.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/11.0-extracting-data-from-receipts-storing-csv.ipynb)

13.  [Building Your Own Automation Scripts](notebooks/12.0-building-your-own-automation-scripts.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/12.0-building-your-own-automation-scripts.ipynb)

14.  [Automatic Downloads: Examples](notebooks/13.0-automatic-downloads-examples.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/13.0-automatic-downloads-examples.ipynb)

15.  [AI Tools: LLM APIs](notebooks/2.0-ai-tools-llm-apis.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/2.0-ai-tools-llm-apis.ipynb)

16.  [File Management Automations](notebooks/3.0-file-management-automations.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/3.0-file-management-automations.ipynb)

17.  [Automation Frameworks and Recipes](notebooks/4.0-automation-frameworks-and-recipes.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/4.0-automation-frameworks-and-recipes.ipynb)

18.  [Automating Your Browser](notebooks/5.0-automating-your-browser.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/5.0-automating-your-browser.ipynb)

19.  [Automating Data Extraction with LLMs](notebooks/6.0-automating-data-extraction-with-llms.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/6.0-automating-data-extraction-with-llms.ipynb)

20.  [Automating Data Extraction from Websites](notebooks/6.1-automating-data-extraction-from-websites.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/6.1-automating-data-extraction-from-websites.ipynb)

21.  [Automating Data Extraction for Product Information](notebooks/6.2-automating-data-extraction-for-product-information.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/6.2-automating-data-extraction-for-product-information.ipynb)

22.  [Introduction to APIs: Using AI APIs (OpenAI, Claude, Llama3)](notebooks/7.0-introduction-to-apis-using-AI-apis-openai-claude-llama3.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/7.0-introduction-to-apis-using-AI-apis-openai-claude-llama3.ipynb)

23.  [Building Automation Workflows with AI](notebooks/8.0-building-automation-workflows-with-ai.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/8.0-building-automation-workflows-with-ai.ipynb)

24.  [Building Email Assistant](notebooks/9.0-building-email-assistant.ipynb)  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/EnkrateiaLucca/oreilly_live_training_agents/blob/main/notebooks/9.0-building-email-assistant.ipynb)
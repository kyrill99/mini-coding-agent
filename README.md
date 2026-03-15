# 🤖 Mini Coding Agent (Built from Scratch)

A lightweight, autonomous software engineering agent built entirely from scratch in pure Python.

This project strips away heavy frameworks like LangChain or AutoGen to demonstrate the first principles of AI agents: an LLM running in a continuous loop, using custom tools to plan, write code, execute terminal commands, and fix its own bugs until the job is done.

## ✨ Key Features

- **Zero-Framework Architecture:** Built with just the `openai` Python SDK to demonstrate how agentic loops work under the hood.
- **Autonomous Planning:** Uses a built-in Todo list tool to break down complex tasks and cross them off as it progresses.
- **Read & Write Access:** Can read existing files to understand context and write new code directly to your drive.
- **Self-Healing Execution:** Runs shell commands to test its own code. If a script crashes, the agent reads the `stderr` output, fixes the bug, and re-tests autonomously.
- **Beautiful CLI:** Uses the `rich` library for a clean, color-coded terminal experience.

## 🧠 How it Works

The agent relies on a simple but powerful "Agent Loop." It takes a user prompt, sends it to the LLM, and if the LLM decides to call a tool, the script executes that Python function and feeds the result back to the LLM. This repeats until the final goal is met.

**Available Tools:**

- `create_todos` / `mark_complete`: For task management.
- `read_file` / `write_file`: For code generation and context.
- `run_terminal_command`: For testing and environment interaction.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- An OpenAI API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/mini-coding-agent.git](https://github.com/YOUR_USERNAME/mini-coding-agent.git)
   cd mini-coding-agent
   ```

````

2. **Install dependencies:**
```bash
pip install -r requirements.txt

````

3. **Set up your environment:**
   Create a `.env` file in the root directory and add your API key:

```env
OPENAI_API_KEY=sk-your-api-key-here

```

## 💻 Usage

Run the agent directly from your terminal:

```bash
python3 agent.py

```

The agent will greet you and ask what you want to build. Try prompts like:

- _"Write a Python script called 'math_utils.py' that calculates the factorial of a number. Then write 'test.py' to verify it works."_
- _"Create a simple HTML/CSS landing page for a coffee shop and save it to an 'output' folder."_
- _"Write a python script that fetches the current price of Bitcoin and run it."_

## 🕵️‍♂️ Example Run

Here is an actual trace of the agent autonomously planning, writing, debugging, and testing a machine learning class from a single prompt:

> > **Starting Autonomous Agent...**
>
> > **What would you like the agent to build today?**
> > `> Write a python class that implements PCA`
>
> **Agent is analyzing the request and planning...**
> Todo #1: Research the PCA algorithm to understand its components and steps.
> Todo #2: Create a Python class named PCA.
> Todo #3: Implement a method in the class to fit the PCA model on the data.
> Todo #4: Implement a method to transform the data using the computed PCA components.
> Todo #5: Test the PCA class with some sample data to ensure it works correctly.
>
> **Update:** Researched the PCA (Principal Component Analysis) algorithm. It involves standardizing the data, computing covariance matrix, finding eigenvalues and eigenvectors, sorting eigenvectors, and transforming the data onto a new subspace.
> Todo #1: ~~Research the PCA algorithm to understand its components and steps.~~
> Todo #2: Create a Python class named PCA.
> _(...)_
>
> **Agent wrote to file:** `pca.py`
> **Update:** Created a Python class named PCA with an initialization method to set the number of components...
> Todo #1: ~~Research the PCA algorithm to understand its components and steps.~~
> Todo #2: ~~Create a Python class named PCA.~~
> _(...)_
>
> _(Agent continues to implement fit and transform methods, crossing off Todo #3 and #4)_
>
> **Agent wrote to file:** `test_pca.py`
> **Agent running command:** `python test_pca.py`
> **Agent running command:** `python3 test_pca.py`
> **Agent running command:** `pip install numpy` _(Agent hits an error, realizes it needs numpy, and installs it autonomously!)_
> **Agent running command:** `python3 test_pca.py`
>
> **Update:** Tested the PCA class using sample data. The class successfully fit the data and transformed it, demonstrating the functionality of dimensional reduction.
> Todo #1: ~~Research the PCA algorithm to understand its components and steps.~~
> Todo #2: ~~Create a Python class named PCA.~~
> Todo #3: ~~Implement a method in the class to fit the PCA model on the data.~~
> Todo #4: ~~Implement a method to transform the data using the computed PCA components.~~
> Todo #5: ~~Test the PCA class with some sample data to ensure it works correctly.~~
>
> **Final Output:**
> The PCA class was successfully implemented and tested. It includes methods to fit the model and transform the data, leading to effective dimensionality reduction. During testing, the sample data was correctly transformed into its principal component representation.

## ⚠️ Security Warning

**Please read before running!** This agent uses Python's `subprocess` module to execute terminal commands autonomously on your host machine.

- Do not ask the agent to perform destructive tasks (e.g., deleting root directories).
- Run this within a Virtual Machine, Docker container, or isolated WSL environment if you plan to give it highly complex or untrusted tasks.

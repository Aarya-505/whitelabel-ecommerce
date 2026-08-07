# Git & Antigravity Workflow Guide

Welcome to the White-Label E-Commerce Platform project! This document outlines our standard Git workflow using Google Antigravity. Because we are a small team, we are using the **GitHub Flow** strategy. This means we have one stable `main` branch, and all new work happens on temporary feature branches.

## 1. Team Delegation & Focus Areas
To prevent us from accidentally overwriting each other's code (merge conflicts), everyone is assigned a specific domain of our Django application. 

| Team Member | Domain | Key Responsibilities |
| :--- | :--- | :--- |
| **Arya (Lead)** | Architecture | Code review, merging Pull Requests (PRs), and cloud deployment. |
| **Anushka** | Payment & Checkout | Integrating live payment gateways into the `storefront` checkout flow. |
| **Sharayu** | Notifications & Alerts | Building email receipts for customers and low-stock alerts for the `admin_dashboard`. |
| **Sayali** | UI/UX & Branding | Customizing the Bootstrap 5 design, category styling, and shop branding. |

## 2. Setting Up Antigravity (One-Time Setup)
We rely entirely on Antigravity's AI agent to write code and manage Git. To allow Antigravity to interact with GitHub on your behalf, you need to enable the GitHub integration.

Antigravity supports the Model Context Protocol (MCP). 
1. Click the `...` at the top of the editor's agent side panel and select **MCP Servers**.
2. Search for the GitHub server and click **Install**.
3. Follow the on-screen prompts to authenticate with your GitHub account. 
Once installed, resources and tools from the server are automatically available to the editor.

## 3. The Daily Workflow (Prompt-Driven Git)
You do not need to memorize terminal commands. Just talk to the Antigravity agent! 

**Step 1: Start a Feature Branch**
Never work directly on the `main` branch. Always ask the agent to create a new branch from `main` with a descriptive name.
> *"I am starting my task. Please pull the latest code from `main` and create a new branch called `feature/add-stripe-payments`."*

**Step 2: Build and Test**
Ask the agent to write the code for your feature. Build in small increments and have the agent make frequent commits.

**Step 3: Push Your Work**
When your feature is complete and working locally, ask the agent to push it to GitHub:
> *"I am done with this feature. Please commit the latest changes and push this branch to GitHub."*

## 4. Pull Requests & Code Review
Once your code is pushed, you must open a Pull Request (PR) to merge it into `main`. Pull requests create a reviewable record of intent and provide a checkpoint for testing.

1. Go to our GitHub repository in your web browser.
2. Click **Compare & pull request** next to your recently pushed branch.
3. Ensure your PR is small and focused. 
4. Arya will review the code. Once approved, it will be merged into the `main` branch!

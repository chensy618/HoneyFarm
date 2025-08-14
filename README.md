# Hardening Honeypot Technologies in IoT with HoneyFarm Environment

## 📌 Overview

This repository contains the design, implementation, and analysis of **HoneyFarm** — a scalable environment for deploying, managing, and hardening IoT honeypot technologies.
The project aims to improve IoT security through **cyber psychology deception-based defense mechanisms** that can capture malicious activity, analyze attack patterns, and strengthen system resilience. 

---

## 🏗 Architecture

<img width="1163" height="895" alt="Implementation_overview_4" src="https://github.com/user-attachments/assets/56d24d05-a89f-4402-b9d2-85f4263152df" />


* **Components:**

  * Honeypots for various IoT device emulations, such as SSH/Telnet on Cowrie, HTTP on SNARE, PJL on MiniPrint.
  * Upgraded with psychological enhancements such as tailored responses aimed at exploiting emotional states of an attacker after identifying a personality trait based on the latter's command execution sequence. Furthermore, several cognitive biases are also incorporated throughout the system 
  * Data collection and storage pipeline.
  * Threat intelligence and analytics modules.
* **Diagram:**
<img width="10063" height="6063" alt="decoy farm-design" src="https://github.com/user-attachments/assets/812acf62-3a4b-4cbd-8c90-69d7d12b70e4" />

* **Design Notes:**
  The Cowrie nodes are configured to respond according to an a personality trait based on an attackers command execution sequence. The responses are tailored to evoke emotions such as CONFIDENCE, SURPRISE, CONFUSION, FRUSTRATION, SELF_DOUBT. Moreover, the layout and structure of the SSH and Telnet honeypot is configured to mimic a realistic IoT server with fake third party software toolkit and notes. The website is developed to represent the dashboard of a smart home IoT environment and serves as the control center for the devices. In the source code there are cues and fake scripts communicating with SSH/Telnet, and PJL servers, that aim to enhance the illusion of interconnetivity.

---

## 🚀 Deployment

> *Placeholder — Add deployment instructions and environment setup details here.*

* **Prerequisites:**

  * Docker / Kubernetes
  * Python 3.x
  * \[List other dependencies here]
* **Steps:**

  1. Clone the repository:

     ```bash
     git clone https://github.com/your-username/honeyfarm-iot.git
     cd honeyfarm-iot
     ```
  2. Configure environment variables:

     ```bash
     cp .env.example .env
     # Edit with your settings
     ```
  3. Deploy:

     ```bash
     docker-compose up -d
     ```

     *or* deploy to Kubernetes with:

     ```bash
     kubectl apply -f k8s/
     ```
* **Configuration Guide:**
  *Describe how to adjust honeypot settings, network rules, and data sinks.*

---

## 📊 Data Analysis & Threat Intelligence

A customised data analysis dashboard was developed using Plotly Dash, a Python based web framework for interactive data visualization.

![Dashboard_home_page](https://github.com/user-attachments/assets/af7301bf-b52a-4b32-833b-30767848b073)



* **Data Collection:**

  * Log files from honeypots
  * Interaction data analysis
  * User study data analysis
* **Analysis Tools:**

  * Python (plotly, pandas, numPy)
* **Metrics & KPIs:**

  * Number of unique human attackers
  * Command execution sequence analysis
  * Average time spent on honeypot
* **Visualization Examples:**
<img width="729" height="452" alt="interactions" src="https://github.com/user-attachments/assets/b12f9b2c-bd8f-40e9-8793-ed6e49f40748" />


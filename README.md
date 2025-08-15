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

This section explains how to set up and run the HoneyFarm environment (SNARE + Cowrie variants + Miniprint) using Docker Compose.

* **Prerequisites:**
Before you begin, make sure you have the following installed:
  * Docker (with Docker Compose support)
  * Python 3.9+
  * Git
* **Setup Instructions:**

  1. Clone the repository:

     ```bash
     git clone https://github.com/chensy618/HoneyFarm.git
     cd honeyfarm
     ```
  2. Build and start the services:

     ```bash
     docker-compose build
     ```
     ```bash
     docker-compose up -d
     ```
  3. Run SNARE
     The SNARE service requires a separate setup.
     Navigate to the /tanner directory and run the same commands:
     ```bash
     cd tanner
     docker-compose build
     docker-compose up -d
    ```
* **Notes:**
  * Use `docker-compose logs -f <service_name>` to view logs for a specific service.
  * Use `docker-compose stop` to stop all containers.
  * Make sure all required ports are available before starting the services.

## ⚙️ Configuration Guide

This section explains how to adjust **honeypot settings**, **network rules**, and **data sinks** for the current `docker-compose.yml`.

---

### 1) Honeypot Settings
#### SNARE
- **Configuration location**  
  - Place the cloned website folders under `tanner/snare/dist/pages/` so each page is accessible to SNARE.  
    Example:
    ```
    tanner/
      snare/
        dist/
          pages/
            iot_system_cloned/
    ```
#### Cowrie (all variants)
- **Configuration location**  
  - `...-etc` volumes → `/cowrie/cowrie-git/etc` (main config: `cowrie.cfg`)  
  - `...-var` volumes → `/cowrie/cowrie-git/var` (runtime data, logs)
- **Common changes**  
  - Change SSH/Telnet ports: adjust the `ports` mapping in `docker-compose.yml`
  - Modify fake system identity: edit `hostname` and related settings (e.g. `prompt`)  in `cowrie.cfg`
  - Update honeytokens: add/remove files in the honeytoken config (e.g. appliance/cowrie/src/honeytoken/honeyfiles.py) to trigger alerts

#### Miniprint
- **Configuration location**  
  - Bind mounts:  
    - `./log/` → `/app/log/` (incoming print job logs)  
    - `./uploads/` → `/app/uploads/` (uploaded files)
- **Common changes**  
  - Adjust exposed port in `docker-compose.yml` (`9100:9100`)
  - Modify fingerprint to avoid honeypot detection
---

### 2) Network Rules

- **Network definition**  
  - All services are connected to a custom `honeynet` bridge network with a fixed subnet (`192.168.100.0/24`)
  - Each service has a static IP (`ipv4_address`)
- **Common changes**  
  - Change `ipv4_address` for a service (must be unique within subnet)
  - Update `ports` mapping to expose services on different host ports
  - Restrict access using firewall rules (e.g., `iptables`) or cloud security groups

---

### 3) Data Sinks

- **Local logging**  
  - Cowrie logs: in the `...-var` volume under `/cowrie/cowrie-git/var/log/cowrie/`
  - Miniprint logs: `miniprint/log/`
- **SMTP alerts (for honeytokens)**  
  - Controlled by the shared `x-environment` variables:
    ```yaml
    SMTP_FROM: "sender@example.com"
    SMTP_TO: "recipient1@example.com,recipient2@example.com"
    SMTP_USER: "sender@example.com"
    SMTP_PASS: "app_password_here"
    SMTP_SERVER: "smtp.example.com"
    SMTP_PORT: "587"
    ```
  - Change `SMTP_TO` to update recipients
- **External log forwarding**  
  - Optionally add a logging/forwarding container (e.g., ELK stack) and mount the honeypot log volumes into it for analysis.
- **Webhook integration**  
  - For GitHub, configure a repository webhook to receive JSON payloads from the honeypot automatically.

---

### 4) Testing Your Configuration

- **SSH access example**:
  ```bash
  ssh -p 2222 david@localhost
  ssh -p 5900 david@localhost
  ssh -p 5000 david@localhost

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

  * Total interactions per honeypot:
  
 <img width="729" height="452" alt="interactions" src="https://github.com/user-attachments/assets/b12f9b2c-bd8f-40e9-8793-ed6e49f40748" />


 * Top commands used on the lighting node:

 <img width="541" height="404" alt="lighting_top_commands" src="https://github.com/user-attachments/assets/84940581-2134-44e9-83b8-b629557ea79b" />


*Top username and IP on the lighting node:

 <img width="1225" height="458" alt="lighting_username+IP_summary" src="https://github.com/user-attachments/assets/3a99bda5-41ae-4084-a726-8b87191df4db" />


* **Human Attacker Interaction:**

* Interaction data:
  
 <img width="658" height="116" alt="Screenshot 2025-08-14 at 15 41 18" src="https://github.com/user-attachments/assets/19223840-c4b9-402a-b9dd-5ba1a628468f" />

* Username and passwords used:

  <img width="3182" height="1419" alt="username+password-human" src="https://github.com/user-attachments/assets/83b2a714-156a-4c8a-ba7b-4ec5f3e468b8" />




# CyberPrep AI: CISSP Study Companion

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.9+-yellow)
![Status](https://img.shields.io/badge/status-active-success)

## 📡 Mission Statement
**CyberPrep AI** is a personally developed study tool designed to assist in the preparation for the **CISSP (Certified Information Systems Security Professional)** certification. 

Leveraging Generative AI (Google Gemini), this application dynamically generates scenario-based questions across all 8 CISSP domains, providing instant feedback and references to GRC standards (NIST, ISO).

## 🛠️ Technical Architecture
This project demonstrates skills in **Platform Administration**, **AI Integration**, and **Software Security**.

* **Backend:** Python / Flask
* **AI Engine:** Google Gemini Pro (via API)
* **Frontend:** HTML5 / CSS3 (Responsive Dark Mode)
* **Deployment:** Docker-ready (compatible with AWS/Azure app services)

## 🚀 Installation & Usage

### Prerequisites
* Python 3.x
* A free [Google AI Studio API Key](https://aistudio.google.com/)

### Setup Instructions
1.  **Clone the Repository**
    ```bash
    git clone https://gitlab.com/your-username/cyberprep-ai.git
    cd cyberprep-ai
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key**
    * **Option A (Linux/Mac):** `export GEMINI_API_KEY="your_key_here"`
    * **Option B (Windows Powershell):** `$env:GEMINI_API_KEY="your_key_here"`

4.  **Launch Application**
    ```bash
    python app.py
    ```
    Access the tool at `http://127.0.0.1:5000`

## 🔒 Security & GRC Considerations
* **Data Minimization:** No user data is stored persistently.
* **Input Validation:** API inputs are sanitized to prevent injection attacks.
* **Availability:** Designed as a stateless microservice for high availability.

---
*Created by [Your Name]*

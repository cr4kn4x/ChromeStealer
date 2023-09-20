# Chrome Stealer (Windows)

## Description

In this repository, you will find a Python3 implementation of my Chrome Stealer. This piece of code can be used for penetration testing !only! on your own devices!

With the increasing usage of Multi-Factor-Authentication (MFA) stolen credentials become more and more un-attractive for hackers. To bypass MFA, a more sophisticated attack called Session Hijacking gains in Popularity. With this Chrome Stealer, you can steal cookies from Chrome's encrypted storage (SQLite database) to gain a better understanding of this relevant attack vector and how malware can make use of it.

- [X] Cookie Decryption 
- [X] Credentials Decryption
- [X] Result as JSON allows easy data transmission over e.g. HTTPS
- [X] Support for: Chrome, ChromeDev, Chromium, Canary (Version 80+)
- [ ] Credit Card Decryption
- [ ] MacOS, Linux implementation

## Prerequisites

Make sure Python3 is installed on your System.

1. Clone this repository

  ```console
  git clone https://github.com/cr4kn4x/ChromeStealer.git
  ```

3. Open the folder of the cloned repository in your shell

  ```console
  cd ChromeStealer
  ```

2. Initialize Python virtual environment

  ```console
  python python -m venv ./
  ```

 3. Activate virtual environment
  
  ```console
  .\Scripts\Activate.ps1
  ```

  4. Install requirements
  
  ```console
  pip install -r requirements.txt
  ```

  5. Run ChromeStealer
  ```console
  python main.py
  ```



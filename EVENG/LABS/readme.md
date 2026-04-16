## EVE-NG Lab Automation (CI/CD)
This repository contains the configuration files and automation scripts to deploy network labs programmatically using Jenkins and the EVE-NG REST API.
## 🚀 Setup Instructions
## 1. Configure Jenkins Credentials
To keep your EVE-NG login secure, do not hardcode passwords.

   1. Open Jenkins and go to Manage Jenkins > Credentials.
   2. Select the (global) domain and click Add Credentials.
   3. Kind: Username with password.
   4. Username: admin (or your EVE-NG user).
   5. Password: eve (or your EVE-NG password).
   6. ID: eve-ng-login (This must match the ID in the Jenkinsfile).

## 2. Configure Jenkins Pipeline

   1. Create a New Item in Jenkins.
   2. Select Pipeline and give it a name (e.g., EVE-NG-Deployer).
   3. Under the Pipeline section, set Definition to Pipeline script from SCM.
   4. SCM: Git.
   5. Repository URL: Paste your GitHub repo URL.
   6. Branch Specifier: */main.
   7. Script Path: Jenkinsfile.

## 3. Connect GitHub to Local Jenkins (Webhook)
To trigger a lab build automatically on every git push:

   1. Expose Jenkins: If your Jenkins is behind a home router, use a tool like ngrok to create a public URL (e.g., ngrok http 8080).
   2. GitHub Settings: In your GitHub repo, go to Settings > Webhooks > Add webhook.
   3. Payload URL: http://<your-public-ip-or-ngrok>/github-webhook/
   4. Content type: application/json.
   5. Events: Just the push event.

## 4. Verify EVE-NG Environment
Ensure your local Jenkins server can reach your EVE-NG server over the network:

* The Jenkins runner must have Python 3 installed.
* Update the EVE_SERVER_IP variable in the Jenkinsfile to match your lab's IP.
* Ensure the EVE-NG node templates (e.g., vios) defined in topology.yaml are actually installed on your EVE-NG server.

## 🛠 Usage

   1. Modify deploy_lab.py to add or change device connections.
   2. Commit and push changes:
   
   git add .
   git commit -m "Added new core router"
   git push origin main
   
   3. Watch the Jenkins console as it logs into EVE-NG and builds your lab.

## Jenkins pre-requisites
# Additional Jenkins config
```
apt-get update -y
apt-get install python3
apt-get install pipx

```




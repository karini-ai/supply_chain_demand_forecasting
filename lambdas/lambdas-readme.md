
# **Deploying Lambda Functions with AWS ECR & Docker**

This guide explains how to **build, tag, and push** Docker images for the Lambda functions in this repository.  
You can either create an **AWS ECR repository** using the **AWS Console** or via the **AWS CLI**.

---

## **📂 Repository Structure**
When you clone this repository, navigate to the `lambdas/` folder to find the available Lambda functions:

```
supply_chain_demand_forecasting/
│── lambdas/
│   ├── nixtla/                  # Lambda for demand forecasting (Nixtla)
│   │   ├── Dockerfile
│   │   ├── lambda_function.py
│   │   ├── ...
│   ├── order-confirmation-lambda/  # Lambda for order confirmation processing
│       ├── Dockerfile
│       ├── lambda_function.py
│       ├── ...
```

Each Lambda function is containerized using **Docker** and pushed to **AWS ECR**.

---

## **🛠 Step 1: Create an AWS ECR Repository**
Before pushing the Docker image, you need an **Amazon Elastic Container Registry (ECR) repository**.

### **Option 1: Create via AWS Console**
1. Go to the **[AWS ECR Console](https://us-east-1.console.aws.amazon.com/ecr/repositories)**.
2. Click **Create Repository**.
3. Choose **Private Repository**.
4. Set a name, e.g., **order-confirmation-repo**.
5. Select a **region** (default: `us-east-1`).
6. Click **Create**.

### **Option 2: Create via AWS CLI**
You can also create the ECR repo using the CLI. Ensure you have configured the credentials like access key,secret key and access token.
Replace `<AWS_ACCOUNT_ID>` and `<REGION>` with your AWS details.

```bash
aws ecr create-repository --repository-name order-confirmation-repo --region <REGION>
```

✅ After running the command, AWS will return a **repository URI** like:
```
<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/order-confirmation-repo
```

---

## **🛠 Step 2: Authenticate Docker to AWS ECR**
Before pushing, **authenticate Docker** with AWS ECR:

```bash
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
```

✅ If successful, you’ll see:
```
Login Succeeded
```

---

## **🛠 Step 3: Navigate to the Lambda Directory**
After cloning the repository, navigate to the respective Lambda function before running Docker commands.

```bash
cd supply_chain_demand_forecasting/lambdas/order-confirmation-lambda
```

---

## **🛠 Step 4: Build, Tag & Push Docker Image**
Once inside the Lambda directory, follow these steps:

### **1️⃣ Build the Docker Image**
```bash
docker build -t order-confirmation-repo .
```

### **2️⃣ Tag the Image for AWS ECR**
Replace `<AWS_ACCOUNT_ID>` and `<REGION>`:

```bash
docker tag order-confirmation-repo:latest <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/order-confirmation-repo:latest
```

### **3️⃣ Push the Image to AWS ECR**
```bash
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/order-confirmation-repo:latest
```

---

## **✅ Step 5: Verify the Image in AWS ECR**
Once the push is successful, navigate to the **AWS ECR Console** and check your repository.

📌 **You should see something like this:**
![AWS ECR Repo View](../images/aws-ecr-repo-view.png)

---

## **📌 Step 6: Retrieve Push Commands for CI/CD**
If integrating into a CI/CD pipeline, **AWS provides pre-generated push commands**.

You can find them by:
1. Navigating to your **ECR Repository** in AWS Console.
2. Clicking **"View Push Commands"** (as shown below).

📌 **Example Push Commands Window:**
![AWS ECR Push Commands](../images/aws-ecr-push-commands.png)

---

## **🎯 Summary**
- **Create an ECR repository** via AWS Console or CLI.
- **Authenticate Docker to AWS ECR**.
- **Navigate to the correct Lambda folder** (`nixtla/` or `order-confirmation-lambda/`).
- **Build, tag, and push** the Docker image to ECR.
- **Verify the pushed image in AWS ECR Console**.
- **Use AWS push commands** for CI/CD automation.

Your Lambda is now packaged as a Docker container and ready for deployment! 🚀

# 🧾 Receipt Recognition App

An AI-powered app that helps groups split dining bills fairly and effortlessly. Upload a receipt, assign items to individuals, and automatically divide shared fees like tax and tips.


## 🎯 Objective

Make bill splitting simple after group outings. The app:
- 🧾 Recognizes receipt items, tax, and tips
- 👤 Allows assigning items to individuals
- 💸 Splits shared fees fairly
- ✅ Outputs a clear summary of who owes what


## ⚙️ Tech Stack

| Layer        | Tech                         |
|--------------|------------------------------|
| Frontend     | React + TypeScript + Vite    |
| Backend      | AWS Lambda (serverless)      |
| OCR Engine   | AWS Textract (ML-powered)    |
| Optional     | AWS S3 (for image storage)   |


## 📸 Features

- Upload receipt image (from file or camera)
- Uses AWS Textract to extract:
  - 🏪 Store/restaurant name
  - 📅 Date of transaction
  - 🧾 Items + prices
  - 💵 Subtotal, tax, tip, and total
- Assign items to people
- Smart splitting of tax/tip
- Summary of individual costs


## 🔁 System Flow

```txt
[React App] → [AWS Lambda] → [Textract OCR]
         ↘︎                  ↙︎
         (optional S3 storage)

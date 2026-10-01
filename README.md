# NoteConvert AI — MVP

This is Part 3: a runnable MVP foundation for the Telegram bot.

## Included

- `/start`
- 20 configurable free credits
- Main menu
- Multi-image upload session
- Finish/Cancel upload
- OCR/transcription
- Gemini vision option
- Tesseract fallback/option
- Clean notes
- PDF output
- DOCX output
- Summary
- MCQs
- Flashcards
- Credit deduction
- Automatic refund if a paid operation fails
- Referral links
- Referral reward after the referred user completes a successful operation
- SQLite locally, PostgreSQL-ready via `DATABASE_URL`

## Current limitation

Telegram payment/Stars checkout is intentionally NOT wired into this first coding stage.
The credit ledger is ready; payment will be added after we test the free MVP.

## 1. Create the Telegram bot

1. Open Telegram.
2. Open `@BotFather`.
3. Run `/newbot`.
4. Copy the bot token.

## 2. Create project

Extract this folder.

Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

## 3. Configure environment

Copy:

```text
.env.example
```

to:

```text
.env
```

Set:

```text
BOT_TOKEN=your_token
```

For Gemini handwriting/vision:

```text
GEMINI_API_KEY=your_key
OCR_PROVIDER=gemini
```

The current default model is configurable:

```text
GEMINI_MODEL=gemini-3.8-flash
```

You can change the model without changing application code.

## 4. Optional Tesseract OCR

If you want local OCR instead of Gemini for text extraction:

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-hin
```

Then:

```text
OCR_PROVIDER=tesseract
```

For Hindi handwriting, do not assume Tesseract will be accurate. Benchmark it against real pages before using it as the primary provider.

## 5. Run

```bash
python -m app.main
```

Open your bot and send:

```text
/start
```

## 6. First test

- Start the bot.
- Tap Handwritten Notes.
- Send 1–3 clear images.
- Tap Finish Upload.
- Try Clean Notes.
- Try PDF.
- Try Summary.
- Check credits.
- Try the referral link with a second Telegram account.

## 7. Production notes

For real deployment:

- use PostgreSQL
- use Redis + a worker for long jobs
- move uploaded files to object storage
- add automatic cleanup
- add webhook deployment
- add proper migration tooling
- add structured logging
- add monitoring
- add Telegram Stars
- add admin dashboard
- add privacy policy and `/paysupport`

Do not store uploaded documents permanently unless required and disclosed.

## Architecture

```text
Telegram
   |
   v
aiogram Bot
   |
   +--> PostgreSQL
   |
   +--> Upload/session handling
   |
   +--> OCR/vision provider
   |
   +--> PDF/DOCX generator
   |
   +--> Credit ledger
   |
   +--> Referral system
```

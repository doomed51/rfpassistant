# RFP Alignment Assistant

A Streamlit web application that helps consulting teams quickly parse RFPs and generate internal alignment materials.

## Features

- Upload RFP PDFs (up to 10MB)
- AI-powered analysis using Claude 3.5 Sonnet
- Generate structured PDF analysis with:
  - Client problems and challenges
  - Specific requirements
  - Gotchas and ambiguities
  - Timeline with key dates
- Generate Excel workbook with:
  - Next steps for proposal team
  - Strategic alignment questions

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file from example:
```bash
copy .env.example .env
```

3. Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

4. Run the app:
```bash
streamlit run app.py
```

### Streamlit Cloud Deployment

1. Push repository to GitHub
2. Connect to Streamlit Cloud at share.streamlit.io
3. Add secrets in app settings (copy from `.streamlit/secrets.toml.example`)
4. Deploy

## Usage

1. Upload an RFP PDF file
2. Wait for AI analysis (10-30 seconds)
3. Download generated PDF analysis
4. Download Excel alignment questions
5. Upload another RFP or refine results

## Tech Stack

- **Frontend**: Streamlit
- **AI**: Anthropic Claude 3.5 Sonnet
- **PDF Processing**: PyPDF2
- **PDF Generation**: ReportLab
- **Excel Generation**: openpyxl

## License

MIT

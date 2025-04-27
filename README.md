# Summary Bot

This project allows you to summarize text messages using a pre-trained t5-small model from Hugging Face. You can find more information about the model here: [T5-small on Hugging Face](https://huggingface.co/google-t5/t5-small).

## Installation

1. Clone the repository:
```bash
git clone <repository_url>
```
2. Navigate to the `summary_bot` folder:
```bash
cd summary_bot
```
3. Install dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Usage

Run the app with your API token:
```bash
python app.py <API_Token>
```


## Current Limitations

- The model currently works only with English text.
- The model has a limited number of input tokens.

## Future Improvements

- Improve the model for better text compression and remove current token limitations.
- Expand the model to support audio and video file summarization.

## Use Case

- Send multiple text messages from others, and the model will return a summary of these messages.
- Alternatively, directly input text for summarization.

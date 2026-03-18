# Vuesentials

A Vue.js component library platform built with Flask.

![Vuesentials Logo](vuesentials_logo.svg)

## What's Inside?

- Vue.js 3
- Flask & SQLAlchemy
- Component Gallery with Search & Filtering
- Responsive Design
- Dark Mode Support

## Installation

```bash
git clone https://github.com/ecrou-exact/Vuesentials.git
cd Vuesentials
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py -i
```

## Launch

```bash
./launch.sh -d
```

Or manually:

```bash
python app.py
```

Then open: `http://localhost:5000`

## Configuration

Edit `config.py`:

- `SECRET_KEY`: Change this!
- `FLASK_PORT`: Port (default: 5000)
- `SQLALCHEMY_DATABASE_URI`: Database path

## Project Structure

```
Vuesentials/
├── app/
│   ├── components/          # Component features
│   ├── static/              # CSS, JS, images
│   └── templates/           # HTML templates
├── app.py                   # Main app
├── config.py                # Configuration
└── requirements.txt         # Dependencies
```

## Features

✨ Component Gallery  
🔍 Search & Filter  
⭐ Featured Components  
📊 View Tracking  
📱 Responsive  
🌓 Dark Mode

## License

MIT License

# Vuesentials

A modern component library management system built with Vue.js and Flask. Create, organize, and manage reusable UI components with ease.

<p align="center">
  <img src="https://raw.githubusercontent.com/ecrou-exact/Vuesentials/main/doc/vuesentials.png" width="300" alt="Vuesentials logo">
</p>

## Overview

Vuesentials is a web application designed to help developers build and maintain a personal library of reusable Vue.js components. The platform provides tools for creating component documentation, managing code files, and sharing component packages.

## Features

- **Component Management**: Create, edit, and delete components with comprehensive information storage
- **Code Organization**: Store Vue.js code alongside HTML, CSS, and JavaScript implementations
- **Documentation**: Write and display documentation using Markdown format (usage guides, features, requirements)
- **Component Export**: Download components as organized ZIP files with structured file organization
- **Search and Filter**: Find components by category, difficulty level, tags, or title
- **Admin Controls**: Authentication system with admin-level permissions for component management
- **Responsive Design**: Fully responsive interface with light and dark mode support
- **Component Gallery**: Browse all components in an organized grid layout with detailed previews

## Project Structure

The project architecture is inspired by [ptit-crolle](https://github.com/DavidCruciani/ptit-crolle.git).

```
vuesentials/
├── app/
│   ├── components/          # Component-related routes and logic
│   ├── account/            # User account management
│   ├── templates/          # Jinja2 templates
│   │   ├── base.html       # Base template with layout
│   │   ├── sidebar.html    # Navigation sidebar
│   │   ├── components/     # Component-specific templates
│   │   │   ├── list.html   # Component gallery view
│   │   │   ├── detail.html # Component detail page
│   │   │   ├── create.html # Component creation form
│   │   │   └── edit.html   # Component editing form
│   │   └── account/        # Account templates
│   └── models/             # Database models
├── static/
│   ├── css/
│   │   └── base/           # Core stylesheets
│   ├── js/
│   │   ├── external_script/
│   │   ├── components/     # Vue.js components
│   │   │   └── actions/    # Component-related Vue components
│   │   └── external_library/
│   └── images/
├── instance/               # Instance folder with SQLite database
├── scripts/               # Utility scripts (backup, restore)
├── requirements.txt       # Python dependencies
└── config.py             # Configuration file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository

```bash
git clone https://github.com/ecrou-exact/Vuesentials.git
cd Vuesentials
```

2. Create virtual environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Initialize the database

```bash
flask db upgrade
```

5. Run the application

```bash
python run.py
```

The application will be available at `http://127.0.0.1:7009`

## Usage

### Creating a Component

1. Navigate to the "Create" section
2. Fill in component details (title, version, category, difficulty)
3. Add Vue.js code (required) and optional HTML, CSS, JavaScript
4. Write documentation (usage guide, features, requirements)
5. Upload a preview image
6. Add tags for better searchability
7. Submit the form to save the component

### Viewing Components

1. Browse the component gallery on the home page
2. Use filters to narrow down by category, difficulty, or search query
3. Click on a component to view detailed information
4. Access code tabs to view implementation details
5. Read documentation in the dedicated docs tab

### Managing Components

- **Download**: Export components as ZIP files with organized file structure
- **Copy Code**: Copy Vue.js code directly to clipboard
- **Edit**: Update component information and code (admin only)
- **Delete**: Remove components from the library (admin only)

### File Organization

When downloading a component, the ZIP file contains:

```
component-name/
├── vue/
│   └── component.vue
├── html/
│   └── template.html
├── css/
│   └── styles.css
├── javascript/
│   └── script.js
├── docs/
│   ├── usage-guide.md
│   ├── features.md
│   └── requirements.md
├── metadata.json
└── README.md
```

## Database

The application uses SQLite for data storage. Database files are located in the `instance/` directory.

### Backup and Restore

Backup your components:

```bash
python scripts/backup.py -b
```

List available backups:

```bash
python scripts/backup.py -l
```

Restore from backup:

```bash
python scripts/restore.py -i
```

## Authentication

The application includes a user authentication system with role-based access control.

- **Regular Users**: Can browse and download components
- **Admins**: Can create, edit, and delete components

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Frontend**: Vue.js 3, Bootstrap 5
- **Database**: SQLite
- **Code Highlighting**: Highlight.js
- **Markdown Processing**: Marked.js
- **Code Editor**: CodeMirror, EasyMDE
- **Icons**: FontAwesome 6

## Configuration

Edit `config.py` to customize:

- Database settings
- Application secret key
- Upload folder paths
- Session configuration

## License

This software is licensed under MIT License

```
Copyright (C) 2025-2026 CIRCL - Computer Incident Response Center Luxembourg
Copyright (C) 2025-2026 Theo Geffe
```

## Contributing

Contributions are welcome. For major changes, please open an issue first to discuss the proposed changes.

## Support

For issues, questions, or suggestions, please visit the [GitHub repository](https://github.com/ecrou-exact/Vuesentials).

---

**Note**: This project structure and implementation approach are inspired by [ptit-crolle](https://github.com/DavidCruciani/ptit-crolle.git).

##

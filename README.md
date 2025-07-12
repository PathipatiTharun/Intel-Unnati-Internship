# Django Product App

A Django web application for managing products with OCR (Optical Character Recognition) capabilities.

## Features

- Product management (CRUD operations)
- OCR functionality for extracting text from product images
- Search functionality
- Modern web interface

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd product_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start the development server:
```bash
python manage.py runserver
```

5. Open your browser and navigate to `http://127.0.0.1:8000/`

## Usage

- Add products with images
- Use OCR to extract text from product images
- Search through products
- Edit and delete products as needed

## Technologies Used

- Django
- Python
- HTML/CSS
- SQLite (development database)
- OCR libraries

## Project Structure

```
product_app/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── product_app/          # Django project settings
├── products/             # Products app
├── templates/            # HTML templates
└── media/               # Uploaded files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE). 
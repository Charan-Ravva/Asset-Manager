# Asset Manager
The SAC Asset Manager is a desktop-based asset management application designed for the Student Activity Center (SAC) at Central Michigan University.
It provides an efficient way for staff to manage equipment inventory, track asset check-ins and check-outs, and maintain accurate usage history.
This project was built as a real-world, production-style system with a focus on usability, reliability, and clean architecture.

## Key Features
- Centralized dashboard with real-time asset statistics
- Asset check-in and check-out functionality
- Inventory management (add, update, and view assets)
- Complete history tracking of issued equipment
- Role-based access control (Admin and Staff)
- Modern and responsive UI using CustomTkinter
- Lightweight and reliable SQLite database backend

## Technology Stack
- Python – Core application logic
- CustomTkinter – Desktop UI framework
- SQLite – Local relational database
- Pillow (PIL) – Image and icon handling
- Git & GitHub – Version control and collaboration

## Project Structure
Asset-Manager/
├── Pages/              # Application pages (Dashboard, Check-In, Check-Out, etc.)
├── Images/             # Icons and UI images
├── main.py             # Application entry point
├── db_conn.py          # Database connection logic
├── migrate.py          # Database initialization and migrations
├── requirements.txt    # Python dependencies
├── .gitignore
└── README.md

## How to Run the Application
- Clone the repository:
git clone https://github.com/Charan-Ravva/Asset-Manager.git

- Navigate to the project directory:
cd Asset-Manager

- Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

## Install required dependencies
- pip install -r requirements.txt
- Run the application:
- python main.py

## Use Case
This application was developed as a real-world system for the Student Activity Center (SAC) at Central Michigan University**, enabling staff to manage shared equipment efficiently.  

## Author
Sri Charan Ravva
- Master’s Student – Information Systems, Central Michigan University
- GitHub: https://github.com/Charan-Ravva
- LinkedIn: www.linkedin.com/in/sricharanravva

## License
This project is open-source and intended for educational, learning purposes.

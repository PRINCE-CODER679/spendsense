# SpendSense AI - Smart Personal Finance Tracker

A production-quality portfolio project demonstrating full-stack development, data processing, financial analytics, and AI integration.

## Project Overview

SpendSense AI is a smart personal finance management platform where users can manually log expenses or upload bank statements in CSV/XLSX format. The application cleans and processes transaction data, automatically categorizes expenses using a rule-based categorization engine, provides financial analytics through an interactive dashboard, tracks budgets, forecasts monthly spending, detects unusual expenses, and generates personalized financial insights.

## Tech Stack

### Frontend
- React 18
- Vite
- JavaScript
- Tailwind CSS
- Recharts (data visualization)
- Axios (API requests)
- React Router (navigation)
- Lucide React (icons)

### Backend
- Python 3.9+
- FastAPI
- Pydantic
- Pandas (data processing)
- NumPy (numerical operations)
- Motor (async MongoDB driver)

### Database
- MongoDB

### AI
- LLM API integration (optional financial assistant)

## Project Structure

```
spendsense-ai/
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── charts/          # Chart components
│   │   ├── services/        # API service layer
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # Utility functions
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # Entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── backend/
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── services/        # Business logic
│   │   ├── database/        # Database connection
│   │   ├── models/          # Data models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── utils/           # Utility functions
│   │   ├── config.py        # Configuration
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   └── .env.example
│
├── data/                    # Sample data files
└── README.md
```

## Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- MongoDB (local or Atlas) - **Required for transaction functionality**

### Backend Setup

1. Navigate to the backend directory:
```bash
cd spendsense-ai/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file:
```bash
cp .env.example .env
```

6. Edit `.env` with your MongoDB connection string:
```
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=spendsense_ai
FRONTEND_URL=http://localhost:5173
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd spendsense-ai/frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start MongoDB
Make sure MongoDB is running locally or update the connection string in `.env` to use MongoDB Atlas.

### Start Backend

1. Navigate to the backend directory:
```bash
cd spendsense-ai/backend
```

2. Activate the virtual environment (if not already active)

3. Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Start Frontend

1. Navigate to the frontend directory:
```bash
cd spendsense-ai/frontend
```

2. Start the Vite dev server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Development Phases

This project is built incrementally across 10 phases:

- **Phase 1**: Project structure, React/Vite frontend, FastAPI backend, MongoDB connection, health-check API, basic dashboard shell ✓
- **Phase 2**: Transaction CRUD APIs, manual transaction form, transaction table, search/filtering ✓
- **Phase 3**: CSV/XLSX upload, Pandas processing, column normalization, import preview, duplicate detection ✓
- **Phase 4**: Rule-based categorization engine, merchant mappings, keyword matching, manual category correction ✓
- **Phase 6**: Budget creation, budget tracking, budget progress, budget alerts ✓
- **Phase 7**: Spending forecast, category forecasts, monthly prediction, predicted budget overspending ✓
- **Phase 8**: Statistical anomaly detection, unusual transaction detection, insight engine ✓
- **Phase 9**: AI financial assistant, backend financial summary, LLM integration, chat UI
- **Phase 10**: Final polish, responsive design, error handling, testing, README, deployment instructions

## Current Status

**Phase 8 Completed**

✅ Project folder structure created
✅ React/Vite frontend with Tailwind CSS configured
✅ FastAPI backend with MongoDB connection
✅ Health-check API endpoint
✅ Basic dashboard shell with sidebar navigation
✅ All placeholder pages created
✅ Transaction Pydantic schemas and models
✅ Transaction service layer with MongoDB operations
✅ Transaction CRUD API endpoints (POST, GET, PUT, DELETE)
✅ Frontend transaction service with Axios
✅ Transaction form component with validation
✅ Transaction table component with loading/empty states
✅ Delete confirmation dialog
✅ Full Transactions page with search, filters, sorting, pagination
✅ MongoDB indexes for performance
✅ Statement processor service with Pandas
✅ Column normalization for different bank formats
✅ CSV and XLSX file processing
✅ Transaction fingerprint for duplicate detection
✅ Upload API endpoints (preview and confirm)
✅ Frontend upload service
✅ Drag-and-drop upload component
✅ Statement preview table with edit capability
✅ Import confirmation flow
✅ Sample bank statement CSV
✅ Transaction source display (manual/imported)
✅ Import success notification on Transactions page

## API Endpoints

### Health Check
- `GET /` - API information
- `GET /health` - Health check with database status

### Transactions
- `POST /api/transactions` - Create a new transaction
- `GET /api/transactions` - Get all transactions with filtering, search, sorting, and pagination
- `GET /api/transactions/{id}` - Get a specific transaction
- `PUT /api/transactions/{id}` - Update a transaction
- `DELETE /api/transactions/{id}` - Delete a transaction

### Upload
- `POST /api/upload/statement` - Upload and preview bank statement
- `POST /api/upload/confirm` - Confirm and import transactions

### Categorization
- `POST /api/transactions/recategorize` - Re-run categorization on non-manual transactions
- `GET /api/transactions/categories/summary` - Get spending totals by category

### Dashboard
- `GET /api/dashboard/summary` - Get financial summary (income, expenses, savings, savings rate)
- `GET /api/dashboard/category-spending` - Get spending totals by category
- `GET /api/dashboard/monthly-trend` - Get monthly income and expenses trend
- `GET /api/dashboard/daily-spending` - Get daily spending for a specific month
- `GET /api/dashboard/top-categories` - Get top spending categories
- `GET /api/dashboard/month-comparison` - Compare current month with previous month

## Features

### Implemented Features (Phases 1-5)
- ✅ Manual transaction entry with form validation
- ✅ Transaction management (create, read, update, delete)
- ✅ Transaction search by description and merchant
- ✅ Transaction filtering by category and type
- ✅ Transaction sorting by date and amount
- ✅ Transaction pagination
- ✅ Professional transaction table with loading/empty states
- ✅ Delete confirmation dialog
- ✅ MongoDB storage with optimized indexes
- ✅ CSV and XLSX bank statement upload
- ✅ Drag-and-drop file upload interface
- ✅ Automatic column detection and normalization
- ✅ Support for multiple bank statement formats
- ✅ Transaction preview before import
- ✅ Edit transactions during preview
- ✅ Duplicate transaction detection
- ✅ Import confirmation with summary
- ✅ Transaction source tracking (manual/imported)
- ✅ Sample bank statement for testing
- ✅ Rule-based categorization engine with merchant and keyword matching
- ✅ Category confidence scoring system
- ✅ Transaction categorization details (confidence, source, reason)
- ✅ Automatic categorization during import
- ✅ Manual category override protection
- ✅ Bulk recategorization endpoint
- ✅ Category summary API for spending totals
- ✅ Color-coded category badges in frontend
- ✅ Categorization details expansion in tables
- ✅ Financial dashboard with summary cards
- ✅ Total income, expenses, savings, and savings rate calculations
- ✅ Category spending donut/pie chart
- ✅ Income vs expenses bar chart
- ✅ Daily spending area chart
- ✅ Top spending categories with progress bars
- ✅ Recent transactions display
- ✅ Month selector for time-based filtering
- ✅ Month-over-month spending comparison
- ✅ MongoDB aggregation for efficient calculations
- ✅ Responsive dashboard layout
- ✅ Loading skeletons and error states
- ✅ Empty state for no data scenarios

### Planned Features (Future Phases)
- Budget management and tracking
- Spending forecasting
- Unusual expense detection
- Personalized financial insights
- AI financial assistant (optional)

### Security
- No banking credentials stored
- File upload validation
- Environment variables for sensitive data
- Input sanitization
- CORS configuration

## Future Improvements
- User authentication
- Multiple user support
- Receipt image OCR
- Recurring expense detection
- Subscription detection
- Financial goal tracking
- Email alerts
- Mobile application
- Bank API integration

## License

This project is for educational and portfolio purposes.

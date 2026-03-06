# AI Code Analyzer

A full-stack application that provides intelligent code analysis, algorithm detection, complexity analysis, and AI-powered optimization suggestions.

## Features

- **Algorithm Detection** - Automatically identifies sorting, search, and graph algorithms in your code
- **Complexity Analysis** - Calculates Big-O notation and identifies performance bottlenecks
- **AI Optimization** - Generates optimized algorithm alternatives with improved complexity
- **Code Insights** - Provides detailed explanations of how algorithms work and why they may be inefficient
- **Side-by-Side Diff** - Visual comparison between original and optimized code
- **Learning Progress** - Tracks submissions, optimizations found, and algorithms used

## Project Structure

```
Ai_Editor/
├── ai_backend/                      # Spring Boot Backend (Java 21)
│   └── ai_monitor1/
│       └── ai_monitor1/
│           ├── src/main/java/       # Java source code
│           │   └── com/example/ai_monitor1/
│           │       ├── config/      # Configuration classes
│           │       ├── controller/ # REST controllers
│           │       ├── dto/         # Data Transfer Objects
│           │       ├── entity/      # JPA entities
│           │       ├── repository/ # Spring Data repositories
│           │       ├── security/   # Security configurations
│           │       ├── service/    # Business logic
│           │       └── util/        # Utility classes
│           └── pom.xml              # Maven dependencies
│
├── ai_monitor_front/               # React Frontend (Vite + React 19)
│   └── ai_monitor_front/
│       ├── src/
│       │   ├── components/         # React components
│       │   │   ├── analysis/       # Analysis-related components
│       │   │   ├── animations/     # Animation components
│       │   │   ├── diff/           # Code diff viewer
│       │   │   ├── editor/         # Code editor components
│       │   │   ├── layout/         # Layout components
│       │   │   └── progress/        # Progress tracking components
│       │   ├── pages/              # Page components
│       │   ├── services/           # API services
│       │   ├── theme/              # Theme configuration
│       │   └── utils/              # Utility functions
│       ├── package.json            # NPM dependencies
│       └── vite.config.js          # Vite configuration
│
├── Static Analyzer/                 # Python Static Code Analyzer
│   ├── static_analyzer/            # Main analyzer package
│   │   ├── languages/              # Language-specific analyzers
│   │   │   ├── base_analyzer.py
│   │   │   ├── cpp_analyzer.py
│   │   │   ├── java_analyzer.py
│   │   │   ├── javascript_analyzer.py
│   │   │   └── python_analyzer.py
│   │   ├── analyzer.py
│   │   ├── ast_parser.py
│   │   ├── complexity_analyzer.py
│   │   ├── language_detector.py
│   │   ├── pattern_detector.py
│   │   └── utils.py
│   ├── tests/                      # Test files
│   ├── api.py                      # Flask API
│   ├── main.py                     # Entry point
│   └── requirements.txt            # Python dependencies
│
└── LLM Response/                    # LLM Engine (Groq-powered)
    ├── llm_engine/                  # LLM engine package
    │   ├── config.py               # Configuration
    │   ├── engine.py               # Main coordinator
    │   ├── llm_client.py           # Groq API client
    │   ├── prompt_builder.py       # Prompt construction
    │   └── response_parser.py      # Response parsing
    ├── main.py                     # Entry point
    └── requirements.txt            # Python dependencies
```

## Tech Stack

### Frontend

- **React 19** - UI framework
- **Vite** - Build tool
- **MUI (Material UI)** - Component library
- **Monaco Editor** - Code editor (same as VS Code)
- **Framer Motion** - Animations
- **React Router** - Client-side routing

### Backend

- **Spring Boot 3.3.5** - Java web framework
- **Java 21** - Programming language
- **Spring Security** - Security framework
- **Spring Data JPA** - ORM framework
- **MySQL** - Database
- **JWT** - Authentication

### Static Analyzer

- **Python** - AST-based code analysis
- **Flask** - Web framework
- **Standard Library Only** - No external dependencies for the core analyzer

### LLM Engine

- **Python** - Programming language
- **Groq API** - LLM inference

## Prerequisites

- Node.js 18+
- Java 21
- Python 3.10+
- Maven
- MySQL (optional, for full functionality)

## Installation & Running

### 1. Start the Python Static Analyzer

```bash
cd Static Analyzer
pip install -r requirements.txt
python run.py
```

The analyzer runs on `http://localhost:5000`

### 2. Start the LLM Response Service (Optional)

```bash
cd "LLM Response"
pip install -r requirements.txt
python main.py
```

The LLM service runs on `http://localhost:5001`

### 3. Start the Spring Boot Backend

```bash
cd ai_backend/ai_monitor1/ai_monitor1
./mvnw spring-boot:run
```

The backend runs on `http://localhost:8080`

### 4. Start the React Frontend

```bash
cd ai_monitor_front/ai_monitor_front
npm install
npm run dev
```

The frontend runs on `http://localhost:5173`

## API Endpoints

### Backend (Port 8080)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Analyze code and return algorithm insights |
| POST | `/api/auth/login` | User authentication |
| POST | `/api/auth/register` | User registration |
| GET | `/api/dashboard` | Get user dashboard data |

#### Analyze Endpoint

**Request Body:**

```json
{
  "code": "your code here",
  "language": "javascript|python|java|cpp"
}
```

**Response:**

```json
{
  "algorithmDetected": "Bubble Sort",
  "timeComplexity": "O(n²)",
  "problem": "Nested loops comparing elements",
  "explanation": "Detailed explanation...",
  "suggestedAlgorithm": "Hash Set Lookup",
  "improvedComplexity": "O(n)",
  "improvedCode": "optimized code here"
}
```

### Static Analyzer (Port 5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/analyze` | Validate code syntax |

### LLM Service (Port 5001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/analyze` | Get AI-powered analysis |

## Pages

### Home Page (`/`)

- Landing page with feature overview
- Quick access to Code Editor and Progress pages

### Analyzer Page (`/analyzer`)

- Full IDE-like interface with:
  - Code editor with syntax highlighting
  - Language selector (JavaScript, Python, Java, C++)
  - Run Analysis button
  - AI Insights sidebar showing:
    - Detected algorithm
    - Time complexity (before/after)
    - Problem identification
    - Detailed explanation
    - Optimized code
  - Side-by-side diff view
  - Resizable bottom panel for results

### Progress Page (`/progress`)

- Learning progress dashboard showing:
  - Total submissions count
  - Optimizations found
  - Average runtime
  - Algorithms detected
  - Weekly activity chart
  - Recent submissions table

### Register Page (`/register`)

- User registration with Google OAuth

## Supported Languages

- JavaScript
- Python
- Java
- C++

## Complexity Analysis

The static analyzer detects the following time complexities:

- **O(1)** - Constant time (no loops)
- **O(log n)** - Logarithmic time (binary search patterns)
- **O(n)** - Linear time (single loop)
- **O(n log n)** - Linearithmic time (merge sort patterns)
- **O(n²)** - Quadratic time (nested loops)
- **O(n³)** - Cubic time (triple nested loops)
- **O(2^n)** - Exponential time (recursion)

## Development

### Frontend Development Server

```bash
cd ai_monitor_front/ai_monitor_front
npm run dev
```

### Backend Development

```bash
cd ai_backend/ai_monitor1/ai_monitor1
./mvnw spring-boot:run
```

### Running Tests (Static Analyzer)

```bash
cd Static Analyzer
pytest
```

## Project Files Overview

### Frontend Components

| Path | Description |
|------|-------------|
| `src/pages/HomePage.jsx` | Landing page |
| `src/pages/AnalyzerPage.jsx` | Code analysis page |
| `src/pages/ProgressPage.jsx` | Learning progress dashboard |
| `src/pages/RegisterPage.jsx` | User registration page |
| `src/components/layout/IDELayout.jsx` | IDE-style layout |
| `src/components/editor/CodeEditor.jsx` | Monaco code editor |
| `src/components/analysis/AIInsightsSidebar.jsx` | Analysis results panel |
| `src/components/diff/CodeDiffViewer.jsx` | Side-by-side code diff |
| `src/components/progress/ProgressCards.jsx` | Progress statistics cards |

### Python Analyzer Modules

| File | Description |
|------|-------------|
| `analyzer.py` | Main entry point |
| `ast_parser.py` | Python AST parsing |
| `complexity_analyzer.py` | Complexity calculation |
| `pattern_detector.py` | Algorithm pattern detection |
| `utils.py` | Helper utilities |

### Backend Java Modules

| Package | Description |
|---------|-------------|
| `controller/` | REST API controllers |
| `service/` | Business logic services |
| `repository/` | Data access layer |
| `entity/` | JPA entities |
| `dto/` | Data transfer objects |
| `config/` | Configuration classes |

## License

This project is for educational and development purposes.


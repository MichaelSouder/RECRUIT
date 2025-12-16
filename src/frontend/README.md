# RECRUIT Frontend

React + TypeScript + Tailwind CSS frontend for the RECRUIT platform.

## Setup

### Prerequisites
- Node.js 18+ (or pnpm)

### Installation

1. Install dependencies:
```bash
npm install
# or
pnpm install
```

2. Create `.env` file (optional):
```bash
VITE_API_URL=http://localhost:8000
```

## Running

### Development
```bash
npm run dev
```

Application will be available at `http://localhost:5173`

## Features

- **Authentication**: Login with JWT tokens
- **Subjects Management**: View, create, edit, delete subjects
- **Studies Management**: View, create, edit, delete studies
- **Search**: Search subjects by name
- **Pagination**: Paginated lists for large datasets
- **Responsive Design**: Mobile-friendly UI with Tailwind CSS

## Test Credentials

- **Admin**: `admin@recruit.test` / `admin123`
- **User**: `user1@recruit.test` / `password123`

## Development

### Code Formatting
```bash
npm run format
```

### Linting
```bash
npm run lint
```

### Build
```bash
npm run build
```

## Project Structure

```
src/
├── api/              # API client and endpoints
├── components/       # Reusable components
│   ├── ui/          # Base UI components
│   └── layout/     # Layout components
├── pages/           # Page components
├── router/          # Routing configuration
├── store/           # State management (Zustand)
├── types/           # TypeScript types
└── utils/           # Utility functions
```



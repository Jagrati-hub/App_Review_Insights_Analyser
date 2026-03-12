# Play Store Review Analyzer - Frontend

Modern Next.js frontend for the Play Store Review Analyzer application.

## Features

- 🎨 Modern UI with Tailwind CSS
- ⚡ Real-time progress tracking
- 📊 Interactive report display
- 📱 Responsive design
- 🔄 Automatic status polling

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **UI**: React 18

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:5000`

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Run the development server:
```bash
npm run dev
# or
yarn dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page (configuration form)
│   ├── globals.css         # Global styles
│   └── report/
│       └── [id]/
│           └── page.tsx    # Report display page
├── public/                 # Static assets
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── tailwind.config.ts     # Tailwind config
└── next.config.js         # Next.js config
```

## API Integration

The frontend connects to the Flask backend API:

- `POST /api/analyze` - Start analysis
- `GET /api/status/<id>` - Get pipeline status
- `GET /api/report/<id>` - Get generated report
- `GET /api/config` - Get configuration limits

## Features

### Configuration Form
- Weeks back selection (8-12)
- Email validation
- Real-time form validation

### Progress Tracking
- Visual progress bar
- Status updates
- Current step display

### Report Display
- Top 3 themes with review counts
- User quotes with styling
- Action ideas
- Email draft preview

## Building for Production

```bash
npm run build
npm start
```

## Environment Variables

Create a `.env.local` file if you need to customize the API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## Customization

### Colors

Edit `tailwind.config.ts` to customize the color scheme:

```typescript
colors: {
  primary: { ... },
  secondary: { ... },
}
```

### Styling

Global styles are in `app/globals.css`. Component-specific styles use Tailwind utility classes.

## Troubleshooting

### CORS Errors

Make sure the Flask backend has CORS enabled for `http://localhost:3000`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"]
    }
})
```

### API Connection Issues

1. Verify Flask backend is running on port 5000
2. Check browser console for errors
3. Ensure API endpoints are accessible

## License

MIT

# Finance AI Dashboard - Frontend

Modern, responsive React/Next.js dashboard for Finance AI expense and budget management.

## Features

- 📊 **Interactive Dashboard** - Real-time KPI cards and charts
- 💰 **Expense Tracking** - View and analyze expenses
- 📈 **Budget Management** - Monitor budget allocations by department
- 📊 **Data Visualization** - Charts, graphs, and KPI metrics
- 🎨 **Modern UI** - Built with Tailwind CSS
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🔄 **Real-time Updates** - Connects to FastAPI backend

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Axios** - API client
- **Zustand** - State management

## Setup

### Prerequisites

- Node.js 18+ and npm/yarn

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Update API URL if needed
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Development

```bash
# Start dev server
npm run dev

# Open browser
# http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
src/
├── components/        # Reusable UI components
│   ├── Layout.tsx    # Main layout wrapper
│   ├── KPICard.tsx   # KPI card component
│   └── Chart.tsx     # Chart components
├── pages/            # Next.js pages/routes
│   ├── _app.tsx      # App wrapper
│   ├── index.tsx     # Dashboard home
│   ├── expenses.tsx  # Expenses page
│   └── budgets.tsx   # Budgets page
├── lib/              # Utilities and helpers
│   └── api.ts        # API client
├── styles/           # Global styles
│   └── globals.css   # Tailwind styles
└── types/            # TypeScript types (coming soon)
```

## API Integration

The dashboard connects to the FastAPI backend at `http://localhost:8000/api/v1`.

### Demo Endpoints

- `GET /demo/all` - All demo data
- `GET /demo/expenses` - Expense data
- `GET /demo/marketing` - Marketing campaigns
- `GET /demo/budgets` - Budget allocations
- `GET /demo/forecasts` - Expense forecasts

### Adding New Pages

1. Create a new file in `src/pages/`
2. Import `Layout` component
3. Fetch data from API using `dashboardAPI` utility
4. Build UI with components

Example:

```tsx
import { Layout } from '@/components/Layout';
import { dashboardAPI } from '@/lib/api';

export default function NewPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    dashboardAPI.getExpenses().then(res => setData(res.data.data));
  }, []);

  return (
    <Layout>
      {/* Your content here */}
    </Layout>
  );
}
```

## Styling

Uses Tailwind CSS with custom color palette:

- **Primary**: Sky blue (#0ea5e9)
- **Success**: Green (#10b981)
- **Warning**: Amber (#f59e0b)
- **Danger**: Red (#ef4444)

Customize in `tailwind.config.js`.

## Performance

- Server-side rendering with Next.js
- Image optimization
- Code splitting
- CSS minification

## Deployment

### Vercel (Recommended)

```bash
# Connect GitHub repo and deploy
# https://vercel.com/new
```

### Docker

```bash
# Build image
docker build -t finance-ai-frontend .

# Run container
docker run -p 3000:3000 finance-ai-frontend
```

### Environment Variables

Set in deployment platform:

- `NEXT_PUBLIC_API_URL` - Backend API URL

## Troubleshooting

**CORS errors?**
- Check backend CORS configuration
- Ensure `NEXT_PUBLIC_API_URL` matches backend

**Data not loading?**
- Verify backend is running on port 8000
- Check browser console for errors
- Confirm demo mode is enabled (`USE_SHEETS_FOR_DEMO=true`)

**Port already in use?**
```bash
# Use different port
npm run dev -- -p 3001
```

## Contributing

- Follow existing code style
- Use TypeScript for new code
- Test components before committing
- Update this README for new features

## License

Private - Recykal Finance AI

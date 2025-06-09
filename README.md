# CES Pipeline Monitor

A real-time monitoring dashboard for the CES (Campaign Effectiveness Score) pipeline, built with React, TypeScript, and Supabase.

## Features

- Real-time monitoring of CES pipeline sensors
- Performance metrics visualization (accuracy, latency, throughput)
- Model status tracking
- One-click model retraining
- Historical metrics analysis

## Tech Stack

- Frontend:
  - React 18
  - TypeScript
  - Tailwind CSS
  - Recharts for data visualization
  - React Query for data fetching
  - React Router for navigation

- Backend:
  - Supabase for database and authentication
  - Edge Functions for serverless operations
  - PostgreSQL for data storage

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/ces-monitor.git
   cd ces-monitor
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

## Database Schema

The application uses the following tables:

- `sensors`: Tracks the status of individual pipeline sensors
- `metric_history`: Stores historical performance metrics
- `model_status`: Current state of the CES model
- `retraining_jobs`: Manages model retraining operations

## Development

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run lint`: Run ESLint
- `npm run test`: Run tests

## Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. Deploy to your hosting platform of choice (e.g., Vercel, Netlify)

3. Set up Supabase:
   - Create a new Supabase project
   - Run the migrations in `supabase/migrations`
   - Deploy the Edge Functions in `supabase/functions`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT

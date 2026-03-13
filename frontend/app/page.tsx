'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

const API_BASE_URL = 'http://localhost:5000/api';

interface Config {
  min_weeks: number;
  max_weeks: number;
  max_themes: number;
  word_limit: number;
  groq_model: string;
}

export default function Home() {
  const router = useRouter();
  const [config, setConfig] = useState<Config | null>(null);
  const [weeksBack, setWeeksBack] = useState(10);
  const [recipientEmail, setRecipientEmail] = useState('team@example.com');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch configuration
    axios.get(`${API_BASE_URL}/config`)
      .then(response => setConfig(response.data))
      .catch(err => console.error('Failed to fetch config:', err));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        weeks_back: weeksBack,
        recipient_email: recipientEmail
      });

      if (response.data.request_id) {
        router.push(`/report/${response.data.request_id}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'An error occurred');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="card bg-white border-2 border-blue-600 mb-8 shadow-xl">
          <div className="border-l-8 border-blue-600 pl-6">
            <h1 className="text-4xl font-bold mb-2 text-slate-800">
              📊 Play Store Review Analyzer
            </h1>
            <p className="text-slate-600 text-lg font-medium">
              Weekly Pulse Reports from User Reviews
            </p>
          </div>
        </header>

        {/* Main Form */}
        <div className="card bg-white border border-slate-200 shadow-xl">
          <div className="border-l-4 border-blue-600 pl-6 mb-6">
            <h2 className="text-2xl font-bold text-slate-800">
              Configure Analysis
            </h2>
          </div>
          <p className="text-slate-600 mb-6 leading-relaxed">
            Generate a weekly pulse report from Google Play Store reviews for the Groww app.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Weeks Back */}
            <div>
              <label htmlFor="weeksBack" className="label text-slate-700 font-semibold">
                Weeks Back
              </label>
              <input
                type="number"
                id="weeksBack"
                value={weeksBack}
                onChange={(e) => setWeeksBack(parseInt(e.target.value))}
                min={config?.min_weeks || 8}
                max={config?.max_weeks || 12}
                className="input bg-white border-2 border-slate-300 text-slate-800 focus:border-blue-600 focus:ring-2 focus:ring-blue-200"
                required
              />
              <p className="text-sm text-slate-500 mt-1">
                Number of weeks to analyze ({config?.min_weeks || 8}-{config?.max_weeks || 12})
              </p>
            </div>

            {/* Recipient Email */}
            <div>
              <label htmlFor="recipientEmail" className="label text-slate-700 font-semibold">
                Recipient Email
              </label>
              <input
                type="email"
                id="recipientEmail"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                className="input bg-white border-2 border-slate-300 text-slate-800 focus:border-blue-600 focus:ring-2 focus:ring-blue-200"
                required
              />
              <p className="text-sm text-slate-500 mt-1">
                Email address to send the report to
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border-2 border-red-500 text-red-800 px-4 py-3 rounded-lg font-medium">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn bg-blue-600 hover:bg-blue-700 text-white font-semibold w-full disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transition-all duration-300 border-2 border-blue-700"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating Report...
                </span>
              ) : (
                'Generate Report'
              )}
            </button>
          </form>
        </div>

        {/* Info Card */}
        <div className="card bg-white border border-slate-200 shadow-xl">
          <div className="border-l-4 border-emerald-600 pl-6 mb-4">
            <h3 className="text-xl font-bold text-slate-800">
              What This Tool Does
            </h3>
          </div>
          <ol className="list-decimal list-inside space-y-2 text-slate-700 leading-relaxed">
            <li><strong className="text-slate-900">Scrapes Reviews:</strong> Fetches up to 2,000 reviews from Google Play Store</li>
            <li><strong className="text-slate-900">Filters & Cleans:</strong> Removes non-English reviews, emojis, and PII</li>
            <li><strong className="text-slate-900">Analyzes Themes:</strong> Uses Groq LLM to identify top themes</li>
            <li><strong className="text-slate-900">Generates Report:</strong> Creates a concise pulse report (≤250 words)</li>
            <li><strong className="text-slate-900">Drafts Email:</strong> Formats the report as a professional email</li>
          </ol>

          <div className="border-l-4 border-amber-600 pl-6 mt-6 mb-4">
            <h3 className="text-xl font-bold text-slate-800">
              Report Includes
            </h3>
          </div>
          <ul className="list-disc list-inside space-y-2 text-slate-700 leading-relaxed">
            <li>📊 Top 3 themes with review counts and ratings</li>
            <li>💬 3 representative user quotes</li>
            <li>💡 3 actionable roadmap items for the product team</li>
          </ul>
        </div>

        {/* Footer */}
        <footer className="card bg-slate-800 text-center mt-8 shadow-xl border-2 border-slate-700">
          <p className="text-slate-300 font-medium">
            © 2026 Groww Product Team | Powered by Groq LLM
          </p>
        </footer>
      </div>
    </div>
  );
}

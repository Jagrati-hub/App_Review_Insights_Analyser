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
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="card text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-600 mb-2">
            📊 Play Store Review Analyzer
          </h1>
          <p className="text-gray-600 text-lg">
            Weekly Pulse Reports from User Reviews
          </p>
        </header>

        {/* Main Form */}
        <div className="card">
          <h2 className="text-2xl font-bold text-primary-600 mb-6">
            Configure Analysis
          </h2>
          <p className="text-gray-600 mb-6">
            Generate a weekly pulse report from Google Play Store reviews for the Groww app.
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Weeks Back */}
            <div>
              <label htmlFor="weeksBack" className="label">
                Weeks Back
              </label>
              <input
                type="number"
                id="weeksBack"
                value={weeksBack}
                onChange={(e) => setWeeksBack(parseInt(e.target.value))}
                min={config?.min_weeks || 8}
                max={config?.max_weeks || 12}
                className="input"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Number of weeks to analyze ({config?.min_weeks || 8}-{config?.max_weeks || 12})
              </p>
            </div>

            {/* Recipient Email */}
            <div>
              <label htmlFor="recipientEmail" className="label">
                Recipient Email
              </label>
              <input
                type="email"
                id="recipientEmail"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                className="input"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Email address to send the report to
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
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
        <div className="card bg-gray-50">
          <h3 className="text-xl font-bold text-primary-600 mb-4">
            What This Tool Does
          </h3>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li><strong>Scrapes Reviews:</strong> Fetches up to 5,000 reviews from Google Play Store</li>
            <li><strong>Filters & Cleans:</strong> Removes non-English reviews, emojis, and PII</li>
            <li><strong>Analyzes Themes:</strong> Uses Groq LLM to identify top themes</li>
            <li><strong>Generates Report:</strong> Creates a concise pulse report (≤250 words)</li>
            <li><strong>Drafts Email:</strong> Formats the report as a professional email</li>
          </ol>

          <h3 className="text-xl font-bold text-primary-600 mt-6 mb-4">
            Report Includes
          </h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            <li>📊 Top 3 themes with review counts</li>
            <li>💬 3 representative user quotes</li>
            <li>💡 3 actionable ideas for the product team</li>
          </ul>
        </div>

        {/* Footer */}
        <footer className="card text-center mt-8">
          <p className="text-gray-600">
            © 2026 Groww Product Team | Powered by Groq LLM
          </p>
        </footer>
      </div>
    </div>
  );
}

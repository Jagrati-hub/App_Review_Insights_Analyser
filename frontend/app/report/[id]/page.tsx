'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

const API_BASE_URL = 'http://localhost:5000/api';

interface Theme {
  rank: number;
  label: string;
  description: string;
  frequency: number;
}

interface Report {
  date_range: [string, string];
  themes: Theme[];
  quotes: string[];
  action_ideas: string[];
  word_count: number;
  review_count: number;
  generation_timestamp: string;
}

interface ReportData {
  request_id: string;
  status: string;
  report?: Report;
  email_draft?: string;
  metadata?: any;
  error?: string;
}

interface Status {
  status: string;
  current_step: string;
  progress_percent: number;
  error_message?: string;
}

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const requestId = params.id as string;
  
  const [status, setStatus] = useState<Status | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!requestId) return;

    const pollStatus = async () => {
      try {
        const statusResponse = await axios.get(`${API_BASE_URL}/status/${requestId}`);
        setStatus(statusResponse.data);

        if (statusResponse.data.status === 'complete') {
          // Fetch report
          const reportResponse = await axios.get(`${API_BASE_URL}/report/${requestId}`);
          setReportData(reportResponse.data);
          setLoading(false);
        } else if (statusResponse.data.status === 'error') {
          setError(statusResponse.data.error_message || 'An error occurred');
          setLoading(false);
        } else {
          // Continue polling
          setTimeout(pollStatus, 2000);
        }
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to fetch report');
        setLoading(false);
      }
    };

    pollStatus();
  }, [requestId]);

  if (loading) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-4xl mx-auto">
          <div className="card text-center">
            <div className="flex flex-col items-center">
              <svg className="animate-spin h-16 w-16 text-primary-500 mb-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <h2 className="text-2xl font-bold text-primary-600 mb-2">
                {status?.current_step || 'Processing...'}
              </h2>
              <div className="w-full max-w-md bg-gray-200 rounded-full h-4 mb-4">
                <div
                  className="bg-gradient-to-r from-primary-500 to-secondary-500 h-4 rounded-full transition-all duration-500"
                  style={{ width: `${status?.progress_percent || 0}%` }}
                />
              </div>
              <p className="text-gray-600">
                {status?.progress_percent || 0}% complete
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-4xl mx-auto">
          <div className="card border-l-4 border-red-500">
            <h2 className="text-2xl font-bold text-red-600 mb-4">❌ Error</h2>
            <p className="text-gray-700 mb-6">{error}</p>
            <Link href="/" className="btn btn-primary">
              Try Again
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!reportData?.report) {
    return null;
  }

  const { report, email_draft, metadata } = reportData;

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="card text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-600 mb-2">
            📊 Weekly Pulse Report
          </h1>
          <div className="text-gray-600 space-y-1">
            <p><strong>Date Range:</strong> {report.date_range[0]} to {report.date_range[1]}</p>
            <p><strong>Reviews Analyzed:</strong> {report.review_count}</p>
            <p><strong>Word Count:</strong> {report.word_count} / 250</p>
          </div>
        </header>

        {/* Top Themes */}
        <div className="card">
          <h3 className="text-2xl font-bold text-primary-600 mb-6">📊 Top Themes</h3>
          <div className="space-y-4">
            {report.themes.map((theme) => (
              <div key={theme.rank} className="border-l-4 border-primary-500 bg-gray-50 p-4 rounded">
                <h4 className="text-lg font-bold text-gray-800 mb-2">
                  {theme.rank}. {theme.label}{' '}
                  <span className="badge">{theme.frequency} reviews</span>
                </h4>
                <p className="text-gray-700">{theme.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* User Voices */}
        <div className="card">
          <h3 className="text-2xl font-bold text-secondary-600 mb-6">💬 User Voices</h3>
          <div className="space-y-4">
            {report.quotes.map((quote, index) => (
              <div key={index} className="border-l-4 border-secondary-500 bg-gray-50 p-4 rounded italic">
                <p className="text-gray-700">"{quote}"</p>
              </div>
            ))}
          </div>
        </div>

        {/* Action Ideas */}
        <div className="card">
          <h3 className="text-2xl font-bold text-primary-600 mb-6">💡 Action Ideas</h3>
          <ol className="list-decimal list-inside space-y-3">
            {report.action_ideas.map((idea, index) => (
              <li key={index} className="bg-gray-50 p-4 rounded text-gray-700">
                {idea}
              </li>
            ))}
          </ol>
        </div>

        {/* Email Draft */}
        <div className="card">
          <h3 className="text-2xl font-bold text-primary-600 mb-6">📧 Email Draft Preview</h3>
          <div className="bg-gray-50 border border-gray-300 rounded p-6 font-mono text-sm whitespace-pre-wrap overflow-x-auto">
            {email_draft}
          </div>
          {metadata?.draft && (
            <p className="text-gray-600 mt-4 text-sm">
              <strong>Recipient:</strong> {metadata.draft.recipient}<br />
              <strong>Saved to:</strong> {metadata.draft.output_path}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="text-center">
          <Link href="/" className="btn btn-secondary">
            Generate Another Report
          </Link>
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

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
      <div className="min-h-screen p-8 bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
        <div className="max-w-4xl mx-auto">
          <div className="card bg-white border-2 border-blue-600 text-center shadow-xl">
            <div className="flex flex-col items-center">
              <svg className="animate-spin h-16 w-16 text-blue-600 mb-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <h2 className="text-2xl font-bold text-slate-800 mb-2">
                {status?.current_step || 'Processing...'}
              </h2>
              <div className="w-full max-w-md bg-slate-200 rounded-full h-4 mb-4 border-2 border-slate-300">
                <div
                  className="bg-gradient-to-r from-blue-600 to-blue-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${status?.progress_percent || 0}%` }}
                />
              </div>
              <p className="text-slate-600 font-medium">
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
      <div className="min-h-screen p-8 bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
        <div className="max-w-4xl mx-auto">
          <div className="card bg-white border-2 border-red-500 border-l-8 shadow-xl">
            <h2 className="text-2xl font-bold text-red-600 mb-4">❌ Error</h2>
            <p className="text-slate-700 mb-6 leading-relaxed">{error}</p>
            <Link href="/" className="btn bg-blue-600 hover:bg-blue-700 text-white font-semibold border-2 border-blue-700">
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
    <div className="min-h-screen p-8 bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="card bg-white border-2 border-blue-600 text-center mb-8 shadow-xl">
          <div className="border-l-8 border-blue-600 pl-6 text-left">
            <h1 className="text-4xl font-bold mb-2 text-slate-800">
              📊 Weekly Pulse Report
            </h1>
            <div className="text-slate-600 space-y-1 font-medium">
              <p><strong className="text-slate-800">Date Range:</strong> {report.date_range[0]} to {report.date_range[1]}</p>
              <p><strong className="text-slate-800">Reviews Analyzed:</strong> {report.review_count}</p>
              <p><strong className="text-slate-800">Word Count:</strong> {report.word_count} / 250</p>
            </div>
          </div>
        </header>

        {/* Top Themes */}
        <div className="card bg-white border border-slate-200 shadow-xl">
          <div className="border-l-4 border-blue-600 pl-6 mb-6">
            <h3 className="text-2xl font-bold text-slate-800">📊 Top Themes</h3>
          </div>
          <div className="space-y-4">
            {report.themes.map((theme) => (
              <div key={theme.rank} className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="text-lg font-bold text-slate-800 mb-2">
                  {theme.rank}. {theme.label}{' '}
                  <span className="badge bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold">{theme.frequency} reviews</span>
                </h4>
                <p className="text-slate-700 leading-relaxed">{theme.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* User Voices */}
        <div className="card bg-white border border-slate-200 shadow-xl">
          <div className="border-l-4 border-emerald-600 pl-6 mb-6">
            <h3 className="text-2xl font-bold text-slate-800">💬 User Voices</h3>
          </div>
          <div className="space-y-4">
            {report.quotes.map((quote, index) => (
              <div key={index} className="border-l-4 border-emerald-500 bg-emerald-50 p-4 rounded-lg italic border border-emerald-200">
                <p className="text-slate-700 leading-relaxed">"{quote}"</p>
              </div>
            ))}
          </div>
        </div>

        {/* Action Ideas */}
        <div className="card bg-white border border-slate-200 shadow-xl">
          <div className="border-l-4 border-amber-600 pl-6 mb-6">
            <h3 className="text-2xl font-bold text-slate-800">💡 Action Roadmap</h3>
          </div>
          <ol className="list-decimal list-inside space-y-3">
            {report.action_ideas.map((idea, index) => (
              <li key={index} className="bg-amber-50 p-4 rounded-lg text-slate-700 border-2 border-amber-200 leading-relaxed font-medium">
                {idea}
              </li>
            ))}
          </ol>
        </div>

        {/* Email Draft */}
        <div className="card bg-white border border-slate-200 shadow-xl">
          <div className="border-l-4 border-indigo-600 pl-6 mb-6">
            <h3 className="text-2xl font-bold text-slate-800">📧 Email Draft Preview</h3>
          </div>
          <div className="bg-slate-50 border-2 border-slate-300 rounded-lg p-6 font-mono text-sm whitespace-pre-wrap overflow-x-auto text-slate-800">
            {email_draft}
          </div>
          {metadata?.draft && (
            <p className="text-slate-600 mt-4 text-sm leading-relaxed">
              <strong className="text-slate-800">Recipient:</strong> {metadata.draft.recipient}<br />
              <strong className="text-slate-800">Saved to:</strong> {metadata.draft.output_path}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="text-center">
          <Link href="/" className="btn bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300 border-2 border-blue-700">
            Generate Another Report
          </Link>
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

/**Premium Settings Page */

import { useState } from 'react';
import { Layout } from '@/components/Layout';
import { Settings, Save, Bell, Shield, Key, User } from 'lucide-react';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('integrations');

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">Settings</h1>
            <p className="mt-1 text-sm text-slate-400">Manage integrations, preferences, and account details</p>
          </div>
          <button className="flex items-center gap-2 rounded-lg bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 transition-colors shadow-sm">
            <Save size={16} /> Save Changes
          </button>
        </div>

        <div className="flex flex-col md:flex-row gap-6">
          {/* Sidebar Tabs */}
          <div className="w-full md:w-64 shrink-0 space-y-1">
            {[
              { id: 'profile', icon: <User size={18} />, label: 'Profile' },
              { id: 'integrations', icon: <Key size={18} />, label: 'Integrations & API' },
              { id: 'notifications', icon: <Bell size={18} />, label: 'Notifications' },
              { id: 'security', icon: <Shield size={18} />, label: 'Security' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-semibold rounded-xl transition-colors ${
                  activeTab === tab.id 
                    ? 'bg-emerald-50 text-emerald-700' 
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <span className={activeTab === tab.id ? 'text-emerald-500' : 'text-slate-400'}>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="flex-1">
            {activeTab === 'integrations' && (
              <div className="space-y-6 animate-fade-in">
                {/* Zoho Books Integration */}
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold text-slate-800 mb-1">Zoho Books Integration</h3>
                  <p className="text-sm text-slate-500 mb-6">Connect your Zoho Books account to sync real-time financial data.</p>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Client ID</label>
                      <input 
                        type="text" 
                        defaultValue="1000.XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                        className="w-full sm:w-96 px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 bg-slate-50 text-slate-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Client Secret</label>
                      <input 
                        type="password" 
                        defaultValue="••••••••••••••••••••••••••••••••"
                        className="w-full sm:w-96 px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 bg-slate-50 text-slate-600"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Organization ID</label>
                      <input 
                        type="text" 
                        defaultValue="654321098"
                        className="w-full sm:w-96 px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 bg-slate-50 text-slate-600"
                      />
                    </div>
                    <div className="pt-2">
                      <button className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors">
                        Test Connection
                      </button>
                    </div>
                  </div>
                </div>

                {/* Google Sheets Integration */}
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold text-slate-800 mb-1">Google Sheets (Marketing)</h3>
                  <p className="text-sm text-slate-500 mb-6">Connect a Google Sheet to pull live marketing spend data.</p>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Spreadsheet ID</label>
                      <input 
                        type="text" 
                        defaultValue="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                        className="w-full sm:w-96 px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 bg-slate-50 text-slate-600"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab !== 'integrations' && (
              <div className="glass-card p-12 text-center text-slate-500 animate-fade-in">
                <Settings size={48} className="mx-auto mb-4 text-slate-300" />
                <h3 className="text-lg font-bold text-slate-700 mb-2">Configuration Pending</h3>
                <p className="text-sm max-w-md mx-auto">This section is currently under development. You will be able to configure {tabLabel(activeTab)} here soon.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}

function tabLabel(id: string) {
  return id === 'profile' ? 'profile settings' : id === 'notifications' ? 'notification preferences' : 'security options';
}

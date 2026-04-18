'use client';

import { useState } from 'react';
import { useSettings } from '@/lib/SettingsContext';
import { 
  Settings as SettingsIcon, Moon, Sun, Bell, Eye, EyeOff, 
  Globe, Calendar, Palette, Shield, Save, Building2, IndianRupee
} from 'lucide-react';

export default function SettingsPage() {
  const { settings, loading, updateSettings } = useSettings();
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'general' | 'dashboard' | 'notifications' | 'privacy' | 'finance'>('general');

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-gray-600 dark:text-gray-300">Loading settings...</div>
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-red-600 dark:text-red-400">Failed to load settings</div>
      </div>
    );
  }

  const handleToggle = async (key: keyof typeof settings, value: boolean) => {
    setSaving(true);
    try {
      await updateSettings({ [key]: value });
    } catch (error) {
      console.error('Error updating setting:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleSelectChange = async (key: keyof typeof settings, value: string) => {
    setSaving(true);
    try {
      await updateSettings({ [key]: value });
    } catch (error) {
      console.error('Error updating setting:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <SettingsIcon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Configure your school preferences and dashboard</p>
        </div>

        {/* School Info Card */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-6 w-6" />
            <h2 className="text-xl font-semibold">School Admin</h2>
          </div>
          <div className="text-2xl font-bold mb-1">{settings.school_name}</div>
          <div className="text-blue-100">Code: {settings.school_code}</div>
        </div>

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex -mb-px">
              {[
                { key: 'general', label: 'General', icon: Globe },
                { key: 'dashboard', label: 'Dashboard', icon: Eye },
                { key: 'notifications', label: 'Notifications', icon: Bell },
                { key: 'privacy', label: 'Privacy', icon: Shield },
                { key: 'finance', label: 'Finance', icon: IndianRupee },
              ].map(tab => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key as any)}
                    className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === tab.key
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="p-6 dark:bg-gray-800">
            {/* General Tab */}
            {activeTab === 'general' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Regional Settings</h3>
                  
                  <div className="space-y-4">
                    {/* Date Format */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <label className="block font-medium mb-2">Date Format</label>
                      <select
                        value={settings.date_format}
                        onChange={(e) => handleSelectChange('date_format', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                        <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                        <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                      </select>
                    </div>

                    {/* Academic Year Format */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <label className="block font-medium mb-2">Academic Year Format</label>
                      <select
                        value={settings.academic_year_format}
                        onChange={(e) => handleSelectChange('academic_year_format', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="YYYY-YYYY">2025-2026</option>
                        <option value="YYYY/YYYY">2025/2026</option>
                        <option value="YY-YY">25-26</option>
                      </select>
                    </div>

                    {/* Timezone */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <label className="block font-medium mb-2">Timezone</label>
                      <input
                        type="text"
                        value={settings.timezone}
                        onChange={(e) => handleSelectChange('timezone', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="UTC"
                      />
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold mb-4">Academic Settings</h3>
                  
                  <div className="space-y-4">
                    {/* Graduation Point */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <label className="block font-medium mb-2">Students Graduate After</label>
                      <select
                        value={settings.graduation_point}
                        onChange={(e) => handleSelectChange('graduation_point', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="10">Grade 10 (High School)</option>
                        <option value="12">Grade 12 (Senior Secondary)</option>
                      </select>
                      <p className="text-sm text-gray-600 mt-2">
                        Choose when students become alumni. If Grade 10, students must explicitly continue to 11-12.
                      </p>
                    </div>
                    
                    {/* Allow Continuation */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-medium">Allow Continuation After Grade 10</div>
                          <div className="text-sm text-gray-600 mt-1">
                            Allow students to continue to grades 11-12 after completing grade 10
                          </div>
                        </div>
                        <button
                          onClick={() => handleToggle('allow_continuation_after_10', !settings.allow_continuation_after_10)}
                          disabled={saving}
                          className={`ml-4 relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            settings.allow_continuation_after_10 ? 'bg-blue-600' : 'bg-gray-200'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              settings.allow_continuation_after_10 ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Dashboard Tab */}
            {activeTab === 'dashboard' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-4">Dashboard Widget Visibility</h3>
                <p className="text-gray-600 mb-4">
                  Control which widgets appear on your dashboard. Even if you own the feature, you can hide it here.
                </p>

                <div className="grid grid-cols-2 gap-4">
                  {[
                    { key: 'show_student_stats', label: 'Student Statistics', desc: 'Total students, enrollment count' },
                    { key: 'show_teacher_stats', label: 'Teacher Statistics', desc: 'Total teachers, assignments' },
                    { key: 'show_alumni_stats', label: 'Alumni Statistics', desc: 'Graduated students count' },
                    { key: 'show_attendance_widget', label: 'Attendance Widget', desc: 'Today\'s attendance summary' },
                    { key: 'show_finance_widget', label: 'Finance Widget', desc: 'Revenue, pending fees' },
                    { key: 'show_health_widget', label: 'Health Widget', desc: 'Medical records overview' },
                    { key: 'show_gatepass_widget', label: 'Gate Pass Widget', desc: 'Active passes today' },
                    { key: 'show_achievements_widget', label: 'Achievements Widget', desc: 'Recent student achievements' },
                    { key: 'show_transfers_widget', label: 'Transfers Widget', desc: 'Pending transfer requests' },
                  ].map(widget => (
                    <div key={widget.key} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="font-medium">{widget.label}</div>
                          <div className="text-sm text-gray-600">{widget.desc}</div>
                        </div>
                        <button
                          onClick={() => handleToggle(widget.key as any, !settings[widget.key as keyof typeof settings])}
                          disabled={saving}
                          className="ml-3"
                        >
                          {settings[widget.key as keyof typeof settings] ? (
                            <Eye className="h-5 w-5 text-green-600" />
                          ) : (
                            <EyeOff className="h-5 w-5 text-gray-400" />
                          )}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-4">Notification Preferences</h3>

                {[
                  { key: 'email_notifications', label: 'Email Notifications', desc: 'Receive updates via email' },
                  { key: 'sms_notifications', label: 'SMS Notifications', desc: 'Receive critical alerts via SMS' },
                  { key: 'push_notifications', label: 'Push Notifications', desc: 'Browser push notifications' },
                ].map(notif => (
                  <div key={notif.key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-medium">{notif.label}</div>
                      <div className="text-sm text-gray-600">{notif.desc}</div>
                    </div>
                    <button
                      onClick={() => handleToggle(notif.key as any, !settings[notif.key as keyof typeof settings])}
                      disabled={saving}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings[notif.key as keyof typeof settings] ? 'bg-blue-600' : 'bg-gray-300'
                      } ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          settings[notif.key as keyof typeof settings] ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Privacy Tab */}
            {activeTab === 'privacy' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold mb-4">Privacy & Data Visibility</h3>
                <p className="text-gray-600 mb-4">
                  Control what sensitive data is displayed to staff members
                </p>

                {[
                  { key: 'show_student_photos', label: 'Student Photos', desc: 'Display student photos in lists and profiles' },
                  { key: 'show_parent_contact', label: 'Parent Contact Info', desc: 'Show parent phone numbers and emails' },
                  { key: 'show_financial_data', label: 'Financial Data', desc: 'Display fee details and payment history' },
                ].map(privacy => (
                  <div key={privacy.key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <div className="font-medium">{privacy.label}</div>
                      <div className="text-sm text-gray-600">{privacy.desc}</div>
                    </div>
                    <button
                      onClick={() => handleToggle(privacy.key as any, !settings[privacy.key as keyof typeof settings])}
                      disabled={saving}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings[privacy.key as keyof typeof settings] ? 'bg-blue-600' : 'bg-gray-300'
                      } ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          settings[privacy.key as keyof typeof settings] ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Finance Tab */}
            {activeTab === 'finance' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Billing Protection</h3>
                  <p className="text-gray-600 mb-4">
                    Configure safeguards to prevent duplicate billing and accidental invoice generation
                  </p>

                  <div className="space-y-4">
                    {[
                      { 
                        key: 'prevent_duplicate_billing', 
                        label: 'Prevent Duplicate Billing', 
                        desc: 'Block creation of duplicate invoices for the same student and installment' 
                      },
                      { 
                        key: 'require_billing_confirmation', 
                        label: 'Require Billing Confirmation', 
                        desc: 'Ask for confirmation twice before generating an invoice' 
                      },
                      { 
                        key: 'show_student_fee_history_on_invoice', 
                        label: 'Show Fee History on Invoice Creation', 
                        desc: 'Display student\'s fee profile when creating new invoices' 
                      },
                    ].map(setting => (
                      <div key={setting.key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-medium">{setting.label}</div>
                          <div className="text-sm text-gray-600">{setting.desc}</div>
                        </div>
                        <button
                          onClick={() => handleToggle(setting.key as any, !settings[setting.key as keyof typeof settings])}
                          disabled={saving}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            settings[setting.key as keyof typeof settings] ? 'bg-emerald-600' : 'bg-gray-300'
                          } ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              settings[setting.key as keyof typeof settings] ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Automation</h3>
                  <p className="text-gray-600 mb-4">
                    Configure automatic invoice generation and payment reminders
                  </p>

                  <div className="space-y-4">
                    {[
                      { 
                        key: 'auto_generate_installment_invoices', 
                        label: 'Auto-Generate Installment Invoices', 
                        desc: 'Automatically create invoices when installment due dates approach' 
                      },
                      { 
                        key: 'auto_apply_late_fee', 
                        label: 'Auto-Apply Late Fees', 
                        desc: 'Automatically add late fee to overdue invoices' 
                      },
                      { 
                        key: 'send_payment_reminders', 
                        label: 'Send Payment Reminders', 
                        desc: 'Send automatic email/SMS reminders for upcoming due dates' 
                      },
                    ].map(setting => (
                      <div key={setting.key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-medium">{setting.label}</div>
                          <div className="text-sm text-gray-600">{setting.desc}</div>
                        </div>
                        <button
                          onClick={() => handleToggle(setting.key as any, !settings[setting.key as keyof typeof settings])}
                          disabled={saving}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            settings[setting.key as keyof typeof settings] ? 'bg-emerald-600' : 'bg-gray-300'
                          } ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              settings[setting.key as keyof typeof settings] ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Invoice Display</h3>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium">Show Fee Breakdown on Invoice</div>
                        <div className="text-sm text-gray-600">Display itemized fee details on printed/PDF invoices</div>
                      </div>
                      <button
                        onClick={() => handleToggle('show_fee_breakdown_on_invoice', !settings.show_fee_breakdown_on_invoice)}
                        disabled={saving}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          settings.show_fee_breakdown_on_invoice ? 'bg-emerald-600' : 'bg-gray-300'
                        } ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            settings.show_fee_breakdown_on_invoice ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Save Indicator */}
        {saving && (
          <div className="fixed bottom-6 right-6 bg-blue-600 text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-2">
            <Save className="h-5 w-5 animate-pulse" />
            <span>Saving...</span>
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface SchoolSettings {
  graduation_point: string | number | readonly string[] | undefined;
  id: number;
  school_name: string;
  school_code: string;
  dark_mode: boolean;
  primary_color: string;

  // Dashboard Widgets
  show_student_stats: boolean;
  show_teacher_stats: boolean;
  show_alumni_stats: boolean;
  show_attendance_widget: boolean;
  show_finance_widget: boolean;
  show_health_widget: boolean;
  show_gatepass_widget: boolean;
  show_achievements_widget: boolean;
  show_transfers_widget: boolean;
  // Gatepass
  enable_gatepass_print: boolean;

  // Notifications
  email_notifications: boolean;
  sms_notifications: boolean;
  push_notifications: boolean;

  // Academic
  academic_year_format: string;
  allow_continuation_after_10: boolean;

  // Privacy
  show_student_photos: boolean;
  show_parent_contact: boolean;
  show_financial_data: boolean;

  // System
  default_language: string;
  timezone: string;
  date_format: string;

  // Finance Settings
  prevent_duplicate_billing: boolean;
  require_billing_confirmation: boolean;
  show_student_fee_history_on_invoice: boolean;
  auto_generate_installment_invoices: boolean;
  days_before_due_to_generate: number;
  auto_apply_late_fee: boolean;
  show_fee_breakdown_on_invoice: boolean;
  send_payment_reminders: boolean;
  reminder_days_before_due: number;

  updated_at: string;
}

interface SettingsContextType {
  settings: SchoolSettings | null;
  loading: boolean;
  updateSettings: (data: Partial<SchoolSettings>) => Promise<void>;
  refreshSettings: () => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<SchoolSettings | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const userStr = localStorage.getItem('user');

      // Skip fetching settings for platform admins (they don't have a school)
      if (userStr) {
        const user = JSON.parse(userStr);
        if (user.user_type === 'PLATFORM_ADMIN') {
          setLoading(false);
          return;
        }
      }

      const response = await axios.get('http://localhost:8000/api/v1/schools/settings/my_settings/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSettings(response.data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = async (data: Partial<SchoolSettings>) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.patch(
        'http://localhost:8000/api/v1/schools/settings/update_my_settings/',
        data,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSettings(response.data);
    } catch (error) {
      console.error('Error updating settings:', error);
      throw error;
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  return (
    <SettingsContext.Provider
      value={{
        settings,
        loading,
        updateSettings,
        refreshSettings: fetchSettings,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
}

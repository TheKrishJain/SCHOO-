'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { usePermissionContext } from '@/lib/rbac-context';
import { 
  Users, UserCheck, DollarSign, ShieldAlert, Calendar, FileText,
  GraduationCap, Clock, TrendingUp, AlertTriangle, Loader2,
  ChevronRight, Trophy, BookOpen
} from 'lucide-react';

interface QuickStat {
  label: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon: React.ReactNode;
  color: string;
  link?: string;
}

interface DashboardWidgetProps {
  title: string;
  children: React.ReactNode;
  module?: string;
  icon?: React.ReactNode;
  link?: string;
  linkLabel?: string;
}

/**
 * Permission-gated dashboard widget wrapper
 */
export function DashboardWidget({ 
  title, 
  children, 
  module, 
  icon,
  link,
  linkLabel = "View All"
}: DashboardWidgetProps) {
  const { hasModuleAccess, isAdmin, loading } = usePermissionContext();

  // If module specified, check permission
  if (module && !loading && !isAdmin && !hasModuleAccess(module)) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <h3 className="font-bold text-gray-800 flex items-center gap-2">
          {icon}
          {title}
        </h3>
        {link && (
          <Link 
            href={link}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
          >
            {linkLabel} <ChevronRight size={16} />
          </Link>
        )}
      </div>
      <div className="p-5">
        {children}
      </div>
    </div>
  );
}

/**
 * Quick stat card with permission gating
 */
export function QuickStatCard({
  stat,
  module,
}: {
  stat: QuickStat;
  module?: string;
}) {
  const { hasModuleAccess, isAdmin, loading } = usePermissionContext();

  if (module && !loading && !isAdmin && !hasModuleAccess(module)) {
    return null;
  }

  const content = (
    <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <div className={`p-2.5 rounded-lg ${stat.color}`}>
          {stat.icon}
        </div>
        {stat.trend && (
          <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
            stat.trend === 'up' ? 'bg-green-100 text-green-700' :
            stat.trend === 'down' ? 'bg-red-100 text-red-700' :
            'bg-gray-100 text-gray-600'
          }`}>
            {stat.change}
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
      <p className="text-sm text-gray-500 mt-1">{stat.label}</p>
    </div>
  );

  if (stat.link) {
    return <Link href={stat.link}>{content}</Link>;
  }

  return content;
}

/**
 * Role-based quick stats grid
 */
export function RoleBasedQuickStats() {
  const { hasModuleAccess, isAdmin, loading: permLoading } = usePermissionContext();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/dashboard/summary/')
      .then(res => {
        setStats(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading || permLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-white p-5 rounded-xl border border-gray-100 animate-pulse">
            <div className="h-10 w-10 bg-gray-200 rounded-lg mb-3" />
            <div className="h-6 w-20 bg-gray-200 rounded mb-2" />
            <div className="h-4 w-28 bg-gray-100 rounded" />
          </div>
        ))}
      </div>
    );
  }

  const allStats: (QuickStat & { module?: string })[] = [
    {
      label: 'Total Students',
      value: stats?.total_students || 0,
      change: '+4%',
      trend: 'up',
      icon: <Users size={20} className="text-blue-600" />,
      color: 'bg-blue-100',
      link: '/dashboard/students',
      module: 'students',
    },
    {
      label: 'Active Teachers',
      value: stats?.active_teachers || 0,
      change: 'Stable',
      trend: 'neutral',
      icon: <GraduationCap size={20} className="text-purple-600" />,
      color: 'bg-purple-100',
      link: '/dashboard/teachers',
      module: 'teachers',
    },
    {
      label: 'Avg Attendance',
      value: `${stats?.avg_attendance || 0}%`,
      change: stats?.attendance_trend || 'Stable',
      trend: 'neutral',
      icon: <UserCheck size={20} className="text-green-600" />,
      color: 'bg-green-100',
      link: '/dashboard/attendance',
      module: 'attendance',
    },
    {
      label: 'Pending Dues',
      value: `₹${(stats?.pending_dues || 0).toLocaleString()}`,
      change: stats?.dues_trend,
      trend: stats?.pending_dues > 50000 ? 'down' : 'neutral',
      icon: <DollarSign size={20} className="text-amber-600" />,
      color: 'bg-amber-100',
      link: '/dashboard/finance',
      module: 'finance',
    },
    {
      label: 'Behavior Incidents',
      value: stats?.total_incidents || 0,
      change: '-12%',
      trend: 'up',
      icon: <ShieldAlert size={20} className="text-red-600" />,
      color: 'bg-red-100',
      link: '/dashboard/discipline',
      module: 'discipline',
    },
    {
      label: 'Active Gate Passes',
      value: stats?.active_passes || 0,
      trend: 'neutral',
      icon: <Clock size={20} className="text-cyan-600" />,
      color: 'bg-cyan-100',
      link: '/dashboard/gatepass',
      module: 'gatepass',
    },
    {
      label: 'Upcoming Exams',
      value: stats?.upcoming_exams || 0,
      trend: 'neutral',
      icon: <FileText size={20} className="text-indigo-600" />,
      color: 'bg-indigo-100',
      link: '/dashboard/academics',
      module: 'academics',
    },
    {
      label: 'Calendar Events',
      value: stats?.upcoming_events || 0,
      trend: 'neutral',
      icon: <Calendar size={20} className="text-pink-600" />,
      color: 'bg-pink-100',
      link: '/dashboard/calendar',
    },
  ];

  // Filter stats based on user's module access
  const visibleStats = allStats.filter(stat => {
    if (isAdmin) return true;
    if (!stat.module) return true;
    return hasModuleAccess(stat.module);
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {visibleStats.map((stat, i) => (
        <QuickStatCard key={i} stat={stat} />
      ))}
    </div>
  );
}

/**
 * Today's attendance summary widget
 */
export function TodayAttendanceWidget() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/attendance/today_summary/')
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <DashboardWidget 
        title="Today's Attendance" 
        module="attendance"
        icon={<UserCheck size={18} className="text-green-500" />}
      >
        <div className="flex justify-center py-8">
          <Loader2 className="animate-spin text-gray-400" size={24} />
        </div>
      </DashboardWidget>
    );
  }

  const presentPct = data?.present_percentage || 0;

  return (
    <DashboardWidget 
      title="Today's Attendance" 
      module="attendance"
      icon={<UserCheck size={18} className="text-green-500" />}
      link="/dashboard/attendance"
    >
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-4xl font-bold text-green-600">{presentPct}%</span>
          <span className="text-sm text-gray-500">Present Today</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div 
            className="h-full bg-green-500 rounded-full transition-all"
            style={{ width: `${presentPct}%` }}
          />
        </div>
        <div className="grid grid-cols-3 gap-2 text-center text-sm">
          <div className="p-2 bg-green-50 rounded-lg">
            <p className="font-bold text-green-700">{data?.present || 0}</p>
            <p className="text-xs text-green-600">Present</p>
          </div>
          <div className="p-2 bg-red-50 rounded-lg">
            <p className="font-bold text-red-700">{data?.absent || 0}</p>
            <p className="text-xs text-red-600">Absent</p>
          </div>
          <div className="p-2 bg-amber-50 rounded-lg">
            <p className="font-bold text-amber-700">{data?.late || 0}</p>
            <p className="text-xs text-amber-600">Late</p>
          </div>
        </div>
      </div>
    </DashboardWidget>
  );
}

/**
 * Recent alerts widget (discipline/incidents)
 */
export function RecentAlertsWidget() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/discipline/incidents/?limit=5&ordering=-created_at')
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : res.data.results || [];
        setAlerts(data.slice(0, 5));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <DashboardWidget 
      title="Recent Incidents" 
      module="discipline"
      icon={<AlertTriangle size={18} className="text-red-500" />}
      link="/dashboard/discipline"
    >
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="animate-spin text-gray-400" size={24} />
        </div>
      ) : alerts.length === 0 ? (
        <p className="text-gray-500 text-sm text-center py-4">No recent incidents</p>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert, i) => (
            <div key={i} className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50">
              <div className={`w-2 h-2 rounded-full mt-2 ${
                alert.severity === 'CRITICAL' ? 'bg-red-500' :
                alert.severity === 'HIGH' ? 'bg-orange-500' :
                'bg-yellow-500'
              }`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{alert.student_name}</p>
                <p className="text-xs text-gray-500 truncate">{alert.description || alert.incident_type}</p>
              </div>
              <span className="text-xs text-gray-400">
                {new Date(alert.created_at).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </DashboardWidget>
  );
}

/**
 * Fee collection summary widget
 */
export function FeeCollectionWidget() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/finance/summary/')
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => {
        // Fallback to invoice totals
        api.get('/finance/invoices/')
          .then(res => {
            const invoices = Array.isArray(res.data) ? res.data : res.data.results || [];
            const collected = invoices.reduce((sum: number, inv: any) => sum + (parseFloat(inv.paid_amount) || 0), 0);
            const pending = invoices.reduce((sum: number, inv: any) => sum + (parseFloat(inv.balance_due) || 0), 0);
            setData({ collected, pending, total: collected + pending });
            setLoading(false);
          })
          .catch(() => setLoading(false));
      });
  }, []);

  return (
    <DashboardWidget 
      title="Fee Collection" 
      module="finance"
      icon={<DollarSign size={18} className="text-green-500" />}
      link="/dashboard/finance"
    >
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="animate-spin text-gray-400" size={24} />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold">Collected</p>
              <p className="text-2xl font-bold text-green-600">₹{(data?.collected || 0).toLocaleString()}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500 uppercase font-semibold">Pending</p>
              <p className="text-xl font-bold text-red-600">₹{(data?.pending || 0).toLocaleString()}</p>
            </div>
          </div>
          {data?.total > 0 && (
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-green-500 rounded-full"
                style={{ width: `${(data.collected / data.total) * 100}%` }}
              />
            </div>
          )}
        </div>
      )}
    </DashboardWidget>
  );
}

/**
 * Top achievers widget
 */
export function TopAchieversWidget() {
  const [achievers, setAchievers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/achievements/?ordering=-created_at&limit=5')
      .then(res => {
        const data = Array.isArray(res.data) ? res.data : res.data.results || [];
        setAchievers(data.slice(0, 5));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <DashboardWidget 
      title="Recent Achievements" 
      module="achievements"
      icon={<Trophy size={18} className="text-yellow-500" />}
      link="/dashboard/achievements"
    >
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="animate-spin text-gray-400" size={24} />
        </div>
      ) : achievers.length === 0 ? (
        <p className="text-gray-500 text-sm text-center py-4">No achievements yet</p>
      ) : (
        <div className="space-y-3">
          {achievers.map((a, i) => (
            <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-yellow-50">
              <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center">
                <Trophy size={14} className="text-yellow-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{a.student_name || a.title}</p>
                <p className="text-xs text-gray-500 truncate">{a.category || a.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </DashboardWidget>
  );
}

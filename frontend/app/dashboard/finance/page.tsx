'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import Link from 'next/link';
import { 
  Plus, Search, DollarSign, CreditCard, FileText, CheckCircle, Clock, 
  AlertCircle, Loader2, X, Users, TrendingUp, Calendar, Receipt,
  ChevronRight, Filter, Eye, Settings, IndianRupee, Wallet, PieChart,
  AlertTriangle, ArrowRight, GraduationCap, Building, BookOpen, History,
  Award, Percent, Banknote
} from 'lucide-react';
import PermissionGate, { IfPermission } from '@/components/PermissionGate';
import { useResourcePermissions } from '@/lib/rbac-context';

// Helper function to format currency in a compact way (L for Lakhs, Cr for Crores)
const formatCurrency = (amount: number, compact = false): string => {
  if (compact) {
    if (amount >= 10000000) return `${(amount / 10000000).toFixed(2)}Cr`;
    if (amount >= 100000) return `${(amount / 100000).toFixed(2)}L`;
  }
  return amount.toLocaleString('en-IN');
};

interface Ledger {
  id: string;
  student: string;
  student_name: string;
  student_suid: string;
  grade_name: string;
  academic_year: string;
  total_charges: string;
  total_payments: string;
  current_balance: string;
  is_cleared: boolean;
}

interface DashboardData {
  total_students: number;
  total_fee_assigned: string;
  total_collected: string;
  total_outstanding: string;
  collection_rate: string;
  pending_invoices: number;
  overdue_invoices: number;
  pending_discounts: number;
  monthly_collection: Array<{month: string; total: string}>;
  collection_by_category: Array<{category: string; total: string}>;
  grade_wise_collection: Array<{grade: string; total_charges: string; total_payments: string}>;
}

export default function FinancePage() {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [assignments, setAssignments] = useState<any[]>([]);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [ledgers, setLedgers] = useState<Ledger[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [schoolId, setSchoolId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'invoices' | 'ledgers' | 'assignments' | 'schedules'>('overview');
  const [statusFilter, setStatusFilter] = useState('ALL');
  
  // RBAC Permissions
  const { canCreate, canEdit } = useResourcePermissions('finance', 'invoice');
  const { canCreate: canRecordPayment } = useResourcePermissions('finance', 'payment');
  
  // Modals
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<any>(null);
  const [paymentForm, setPaymentForm] = useState({ amount: '', mode: 'CASH', reference: '' });
  const [paymentLoading, setPaymentLoading] = useState(false);

  useEffect(() => {
    // First fetch school ID, then fetch all data
    const initializePage = async () => {
      try {
        const settingsRes = await api.get('/schools/settings/my_settings/');
        const fetchedSchoolId = settingsRes.data.school || '';
        setSchoolId(fetchedSchoolId);
        await fetchAllData(fetchedSchoolId);
      } catch (error) {
        console.error('Error fetching school settings:', error);
        setLoading(false);
      }
    };
    initializePage();
  }, []);

  const fetchAllData = async (schoolIdParam?: string) => {
    const currentSchoolId = schoolIdParam || schoolId;
    if (!currentSchoolId) {
      setLoading(false);
      return;
    }
    try {
      const [invoicesRes, assignmentsRes, schedulesRes, ledgersRes, dashboardRes] = await Promise.all([
        api.get('/finance/invoices/', { params: { school: currentSchoolId, academic_year: '2024-2025' } }),
        api.get('/finance/assignments/', { params: { school: currentSchoolId, academic_year: '2024-2025' } }),
        api.get('/finance/schedules/', { params: { school: currentSchoolId } }),
        api.get('/finance/ledgers/', { params: { school: currentSchoolId, academic_year: '2024-2025' } }),
        api.get('/finance/dashboard/', { params: { school: currentSchoolId, academic_year: '2024-2025' } }).catch(() => null)
      ]);
      setInvoices(Array.isArray(invoicesRes.data) ? invoicesRes.data : invoicesRes.data.results || []);
      setAssignments(Array.isArray(assignmentsRes.data) ? assignmentsRes.data : assignmentsRes.data.results || []);
      setSchedules(Array.isArray(schedulesRes.data) ? schedulesRes.data : schedulesRes.data.results || []);
      setLedgers(Array.isArray(ledgersRes.data) ? ledgersRes.data : ledgersRes.data.results || []);
      if (dashboardRes) {
        setDashboardData(dashboardRes.data);
      }
    } catch (e) {
      console.error("Failed to load finance data", e);
    } finally {
      setLoading(false);
    }
  };

  const handleRecordPayment = async () => {
    if (!selectedInvoice) return;
    setPaymentLoading(true);
    try {
      await api.post(`/finance/invoices/${selectedInvoice.id}/record_payment/`, paymentForm);
      setShowPaymentModal(false);
      setPaymentForm({ amount: '', mode: 'CASH', reference: '' });
      fetchAllData();
    } catch (e) {
      alert("Failed to record payment.");
    } finally {
      setPaymentLoading(false);
    }
  };

  const openPaymentModal = (invoice: any) => {
    setSelectedInvoice(invoice);
    setPaymentForm({ ...paymentForm, amount: invoice.balance_due }); 
    setShowPaymentModal(true);
  };

  // Stats Calculation - Use ledger data as primary source
  const totalCollected = ledgers.reduce((sum, l) => sum + (parseFloat(l.total_payments) || 0), 0);
  const totalPending = ledgers.reduce((sum, l) => sum + (parseFloat(l.current_balance) || 0), 0);
  const totalInvoiced = ledgers.reduce((sum, l) => sum + (parseFloat(l.total_charges) || 0), 0);
  const overdueInvoices = invoices.filter(inv => inv.status === 'OVERDUE').length;
  const totalStudentsAssigned = new Set(ledgers.map(l => l.student)).size;
  const collectionRate = totalInvoiced > 0 ? ((totalCollected / totalInvoiced) * 100).toFixed(1) : 0;

  // Filter Logic
  const filteredInvoices = invoices.filter(inv => {
    const matchesSearch = 
      (inv.student_name || "").toLowerCase().includes(search.toLowerCase()) ||
      (inv.invoice_number || "").toLowerCase().includes(search.toLowerCase()) ||
      (inv.student_suid || "").toLowerCase().includes(search.toLowerCase());
    
    const matchesStatus = statusFilter === 'ALL' || inv.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="text-center">
        <Loader2 className="animate-spin w-12 h-12 mx-auto text-blue-600 mb-4" />
        <p className="text-gray-600 font-medium">Loading Financial Data...</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30 pb-20">
      
      {/* ===== HEADER ===== */}
      <div className="bg-white border-b border-gray-100 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-200">
                  <IndianRupee className="text-white" size={20} />
                </div>
                Finance Management
              </h1>
              <p className="text-gray-500 text-sm mt-1">Manage fees, invoices, and payments</p>
            </div>
            
            <div className="flex items-center gap-3">
              <Link href="/dashboard/settings">
                <button className="p-2.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-xl transition-all">
                  <Settings size={20} />
                </button>
              </Link>
              
              {canCreate && (
                <Link href="/dashboard/finance/add">
                  <button className="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-emerald-200 transition-all flex items-center gap-2">
                    <Plus size={18} /> New Invoice
                  </button>
                </Link>
              )}
            </div>
          </div>
          
          {/* Tabs */}
          <div className="flex gap-1 mt-4 bg-gray-100 p-1 rounded-xl w-fit overflow-x-auto">
            {[
              { id: 'overview', label: 'Overview', icon: PieChart },
              { id: 'ledgers', label: 'Student Ledgers', icon: BookOpen },
              { id: 'invoices', label: 'Invoices', icon: FileText },
              { id: 'assignments', label: 'Fee Assignments', icon: Users },
              { id: 'schedules', label: 'Payment Plans', icon: Calendar },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all whitespace-nowrap ${
                  activeTab === tab.id 
                    ? 'bg-white text-gray-900 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <tab.icon size={16} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        
        {/* ===== OVERVIEW TAB ===== */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            
            {/* Stats Grid - Using Dashboard Data */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              
              {/* Total Collected */}
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider">Total Collected</p>
                    <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mt-2 truncate" title={`₹${formatCurrency(totalCollected)}`}>
                      ₹{formatCurrency(totalCollected, true)}
                    </h3>
                    <p className="text-emerald-600 text-sm font-medium mt-1 flex items-center gap-1">
                      <TrendingUp size={14} /> {collectionRate}% collection rate
                    </p>
                  </div>
                  <div className="w-12 h-12 lg:w-14 lg:h-14 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg shadow-emerald-200 flex-shrink-0">
                    <Wallet className="text-white" size={20} />
                  </div>
                </div>
              </div>

              {/* Pending Dues */}
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider">Pending Dues</p>
                    <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mt-2 truncate" title={`₹${formatCurrency(totalPending)}`}>
                      ₹{formatCurrency(totalPending, true)}
                    </h3>
                    <p className="text-amber-600 text-sm font-medium mt-1 flex items-center gap-1">
                      <Clock size={14} /> {invoices.filter(i => i.status !== 'PAID').length} invoices pending
                    </p>
                  </div>
                  <div className="w-12 h-12 lg:w-14 lg:h-14 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg shadow-amber-200 flex-shrink-0">
                    <Clock className="text-white" size={20} />
                  </div>
                </div>
              </div>

              {/* Students Assigned */}
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider">Students Assigned</p>
                    <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mt-2">{totalStudentsAssigned}</h3>
                    <p className="text-blue-600 text-sm font-medium mt-1 flex items-center gap-1">
                      <Users size={14} /> With fee schedules
                    </p>
                  </div>
                  <div className="w-12 h-12 lg:w-14 lg:h-14 bg-gradient-to-br from-blue-400 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-200 flex-shrink-0">
                    <Users className="text-white" size={20} />
                  </div>
                </div>
              </div>

              {/* Overdue */}
              <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-gray-500 text-xs font-semibold uppercase tracking-wider">Overdue Invoices</p>
                    <h3 className="text-2xl lg:text-3xl font-bold text-gray-900 mt-2">{overdueInvoices}</h3>
                    <p className="text-red-600 text-sm font-medium mt-1 flex items-center gap-1">
                      <AlertTriangle size={14} /> Require attention
                    </p>
                  </div>
                  <div className="w-12 h-12 lg:w-14 lg:h-14 bg-gradient-to-br from-red-400 to-red-600 rounded-2xl flex items-center justify-center shadow-lg shadow-red-200 flex-shrink-0">
                    <AlertTriangle className="text-white" size={24} />
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              <Link href="/dashboard/finance/add">
                <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-6 text-white hover:shadow-xl hover:shadow-emerald-200/50 transition-all cursor-pointer group">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-lg">Generate Invoice</h3>
                      <p className="text-emerald-100 text-sm mt-1">Create new invoice for student</p>
                    </div>
                    <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center group-hover:bg-white/30 transition-colors">
                      <Receipt size={24} />
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-4 text-emerald-100 text-sm font-medium">
                    Get started <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>

              <Link href="/dashboard/finance/categories">
                <div className="bg-white rounded-2xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all cursor-pointer group">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-lg text-gray-900">Fee Categories</h3>
                      <p className="text-gray-500 text-sm mt-1">Manage tuition, lab, transport fees</p>
                    </div>
                    <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600 group-hover:bg-blue-100 transition-colors">
                      <DollarSign size={24} />
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-4 text-blue-600 text-sm font-medium">
                    Configure <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>

              <div className="bg-white rounded-2xl p-6 border border-gray-200 hover:border-purple-300 hover:shadow-lg transition-all cursor-pointer group"
                   onClick={() => setActiveTab('assignments')}>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-lg text-gray-900">Bulk Assign Fees</h3>
                    <p className="text-gray-500 text-sm mt-1">Assign fees to entire grade at once</p>
                  </div>
                  <div className="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center text-purple-600 group-hover:bg-purple-100 transition-colors">
                    <GraduationCap size={24} />
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-4 text-purple-600 text-sm font-medium">
                  Assign now <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </div>

            {/* Recent Invoices Preview */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                <h3 className="font-bold text-gray-900">Recent Invoices</h3>
                <button 
                  onClick={() => setActiveTab('invoices')}
                  className="text-blue-600 text-sm font-medium flex items-center gap-1 hover:text-blue-700"
                >
                  View all <ChevronRight size={16} />
                </button>
              </div>
              <div className="divide-y divide-gray-50">
                {invoices.slice(0, 5).map(inv => (
                  <div key={inv.id} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                        inv.status === 'PAID' ? 'bg-emerald-100 text-emerald-600' :
                        inv.status === 'OVERDUE' ? 'bg-red-100 text-red-600' :
                        'bg-amber-100 text-amber-600'
                      }`}>
                        {inv.status === 'PAID' ? <CheckCircle size={20} /> : <Clock size={20} />}
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">{inv.student_name}</p>
                        <p className="text-xs text-gray-500 font-mono">{inv.invoice_number}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-gray-900">₹{parseFloat(inv.total_amount).toLocaleString()}</p>
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                        inv.status === 'PAID' ? 'bg-emerald-100 text-emerald-700' :
                        inv.status === 'OVERDUE' ? 'bg-red-100 text-red-700' :
                        inv.status === 'PARTIAL' ? 'bg-amber-100 text-amber-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {inv.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===== INVOICES TAB ===== */}
        {activeTab === 'invoices' && (
          <div className="space-y-6">
            
            {/* Filters Bar */}
            <div className="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input 
                  type="text" 
                  placeholder="Search by student name, SUID, or invoice #..." 
                  className="w-full pl-11 pr-4 py-3 bg-gray-50 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 bg-gray-100 p-1 rounded-xl">
                  {['ALL', 'UNPAID', 'PARTIAL', 'PAID', 'OVERDUE'].map(status => (
                    <button
                      key={status}
                      onClick={() => setStatusFilter(status)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        statusFilter === status 
                          ? 'bg-white text-gray-900 shadow-sm' 
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Invoice Table */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              {filteredInvoices.length === 0 ? (
                <div className="text-center py-16">
                  <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500 font-medium">No invoices found</p>
                  <p className="text-gray-400 text-sm mt-1">Try adjusting your search or filters</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-100">
                      <tr className="text-xs uppercase text-gray-500 font-semibold">
                        <th className="px-6 py-4 text-left">Invoice</th>
                        <th className="px-6 py-4 text-left">Student</th>
                        <th className="px-6 py-4 text-left">Amount</th>
                        <th className="px-6 py-4 text-left">Paid</th>
                        <th className="px-6 py-4 text-left">Due Date</th>
                        <th className="px-6 py-4 text-left">Status</th>
                        <th className="px-6 py-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {filteredInvoices.map(inv => (
                        <tr key={inv.id} className="hover:bg-gray-50/50 transition-colors">
                          <td className="px-6 py-4">
                            <span className="font-mono text-sm text-gray-600">{inv.invoice_number}</span>
                          </td>
                          <td className="px-6 py-4">
                            <Link href={`/dashboard/finance/student/${inv.student}`}>
                              <div className="hover:text-blue-600 cursor-pointer">
                                <p className="font-semibold text-gray-900">{inv.student_name || "Unknown"}</p>
                                <p className="text-xs text-gray-400 font-mono">{inv.student_suid}</p>
                              </div>
                            </Link>
                          </td>
                          <td className="px-6 py-4 font-bold text-gray-900">
                            ₹{parseFloat(inv.total_amount).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-emerald-600 font-semibold">
                            ₹{parseFloat(inv.paid_amount).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {inv.due_date ? new Date(inv.due_date).toLocaleDateString() : '-'}
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase ${
                              inv.status === 'PAID' ? 'bg-emerald-100 text-emerald-700' :
                              inv.status === 'PARTIAL' ? 'bg-amber-100 text-amber-700' :
                              inv.status === 'OVERDUE' ? 'bg-red-100 text-red-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {inv.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            {inv.status !== 'PAID' && canRecordPayment && (
                              <button 
                                onClick={() => openPaymentModal(inv)}
                                className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-4 py-2 rounded-lg text-xs font-bold hover:shadow-lg hover:shadow-emerald-200 transition-all flex items-center gap-1.5 ml-auto"
                              >
                                <CreditCard size={14} /> Collect
                              </button>
                            )}
                            {inv.status === 'PAID' && (
                              <div className="flex items-center gap-1 justify-end text-emerald-600 text-xs font-bold">
                                <CheckCircle size={16} /> Paid
                              </div>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ===== STUDENT LEDGERS TAB ===== */}
        {activeTab === 'ledgers' && (
          <div className="space-y-6">
            
            {/* Search & Filters */}
            <div className="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input 
                  type="text" 
                  placeholder="Search by student name or SUID..." 
                  className="w-full pl-11 pr-4 py-3 bg-gray-50 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
              </div>
              
              <div className="flex items-center gap-3">
                <select className="px-4 py-2.5 bg-gray-100 rounded-xl text-sm font-medium text-gray-700 outline-none cursor-pointer">
                  <option value="">All Years</option>
                  <option value="2024-25">2024-25</option>
                  <option value="2023-24">2023-24</option>
                </select>
                <select className="px-4 py-2.5 bg-gray-100 rounded-xl text-sm font-medium text-gray-700 outline-none cursor-pointer">
                  <option value="">All Grades</option>
                  <option value="10">Grade 10</option>
                  <option value="9">Grade 9</option>
                </select>
              </div>
            </div>

            {/* Ledger Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl p-5 text-white">
                <div className="flex items-center gap-3">
                  <div className="bg-white/20 rounded-xl p-2">
                    <Users size={20} />
                  </div>
                  <div>
                    <p className="text-sm text-emerald-100">Total Students</p>
                    <p className="text-2xl font-bold">{ledgers.filter((l, i, arr) => arr.findIndex(x => x.student === l.student) === i).length}</p>
                  </div>
                </div>
              </div>
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-5 text-white">
                <div className="flex items-center gap-3">
                  <div className="bg-white/20 rounded-xl p-2">
                    <BookOpen size={20} />
                  </div>
                  <div>
                    <p className="text-sm text-blue-100">Total Ledgers</p>
                    <p className="text-2xl font-bold">{ledgers.length}</p>
                  </div>
                </div>
              </div>
              <div className="bg-gradient-to-br from-amber-500 to-orange-500 rounded-2xl p-5 text-white">
                <div className="flex items-center gap-3">
                  <div className="bg-white/20 rounded-xl p-2">
                    <AlertTriangle size={20} />
                  </div>
                  <div>
                    <p className="text-sm text-amber-100">Pending Balance</p>
                    <p className="text-2xl font-bold">{ledgers.filter(l => !l.is_cleared).length}</p>
                  </div>
                </div>
              </div>
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-5 text-white">
                <div className="flex items-center gap-3">
                  <div className="bg-white/20 rounded-xl p-2">
                    <CheckCircle size={20} />
                  </div>
                  <div>
                    <p className="text-sm text-green-100">Cleared Ledgers</p>
                    <p className="text-2xl font-bold">{ledgers.filter(l => l.is_cleared).length}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Ledgers Table */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <h3 className="font-bold text-gray-900">Student Fee Ledgers</h3>
                <span className="text-sm text-gray-500">{ledgers.length} ledgers</span>
              </div>
              
              {ledgers.length === 0 ? (
                <div className="p-12 text-center">
                  <BookOpen size={48} className="mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500">No ledgers found</p>
                  <p className="text-sm text-gray-400 mt-1">Fee ledgers will appear here when students have fee assignments</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left p-4 text-xs font-semibold text-gray-500 uppercase">Student</th>
                        <th className="text-left p-4 text-xs font-semibold text-gray-500 uppercase">Grade</th>
                        <th className="text-left p-4 text-xs font-semibold text-gray-500 uppercase">Academic Year</th>
                        <th className="text-right p-4 text-xs font-semibold text-gray-500 uppercase">Total Charges</th>
                        <th className="text-right p-4 text-xs font-semibold text-gray-500 uppercase">Payments</th>
                        <th className="text-right p-4 text-xs font-semibold text-gray-500 uppercase">Balance</th>
                        <th className="text-center p-4 text-xs font-semibold text-gray-500 uppercase">Status</th>
                        <th className="text-center p-4 text-xs font-semibold text-gray-500 uppercase">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {ledgers
                        .filter(ledger => 
                          !search || 
                          ledger.student_name?.toLowerCase().includes(search.toLowerCase()) ||
                          ledger.student_suid?.toLowerCase().includes(search.toLowerCase())
                        )
                        .slice(0, 20)
                        .map(ledger => (
                        <tr key={ledger.id} className="hover:bg-gray-50 transition-colors">
                          <td className="p-4">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-sm">
                                {ledger.student_name?.[0] || '?'}
                              </div>
                              <div>
                                <p className="font-semibold text-gray-900">{ledger.student_name}</p>
                                <p className="text-xs text-gray-500">{ledger.student_suid}</p>
                              </div>
                            </div>
                          </td>
                          <td className="p-4 text-sm text-gray-600">{ledger.grade_name || '-'}</td>
                          <td className="p-4">
                            <span className="px-2.5 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-lg">
                              {ledger.academic_year}
                            </span>
                          </td>
                          <td className="p-4 text-right font-medium text-gray-900">
                            ₹{parseFloat(ledger.total_charges || '0').toLocaleString('en-IN')}
                          </td>
                          <td className="p-4 text-right font-medium text-emerald-600">
                            ₹{parseFloat(ledger.total_payments || '0').toLocaleString('en-IN')}
                          </td>
                          <td className="p-4 text-right font-bold text-gray-900">
                            ₹{parseFloat(ledger.current_balance || '0').toLocaleString('en-IN')}
                          </td>
                          <td className="p-4 text-center">
                            {ledger.is_cleared ? (
                              <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 text-xs font-medium rounded-lg inline-flex items-center gap-1">
                                <CheckCircle size={12} /> Cleared
                              </span>
                            ) : (
                              <span className="px-2.5 py-1 bg-amber-50 text-amber-700 text-xs font-medium rounded-lg inline-flex items-center gap-1">
                                <Clock size={12} /> Pending
                              </span>
                            )}
                          </td>
                          <td className="p-4 text-center">
                            <Link href={`/dashboard/finance/ledger/${ledger.student}`}>
                              <button className="px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg text-xs font-medium hover:bg-blue-100 transition-colors inline-flex items-center gap-1">
                                <History size={14} /> View History
                              </button>
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ===== ASSIGNMENTS TAB ===== */}
        {activeTab === 'assignments' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
              <h3 className="font-bold text-lg text-gray-900 mb-4">Student Fee Assignments</h3>
              <p className="text-gray-500 text-sm mb-6">
                Students with assigned fee schedules. Click on a student to view their complete fee profile.
              </p>
              
              <div className="grid gap-4">
                {assignments.slice(0, 10).map(assignment => (
                  <Link key={assignment.id} href={`/dashboard/finance/student/${assignment.student}`}>
                    <div className="p-4 border border-gray-200 rounded-xl hover:border-blue-300 hover:shadow-md transition-all cursor-pointer flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">
                          {assignment.student_name?.[0] || '?'}
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900">{assignment.student_name}</p>
                          <p className="text-xs text-gray-500">
                            <span className="font-mono">{assignment.student_suid}</span>
                            <span className="mx-2">•</span>
                            {assignment.fee_schedule_name}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-gray-900">₹{parseFloat(assignment.net_payable || 0).toLocaleString()}</p>
                        <p className="text-xs">
                          <span className="text-emerald-600 font-semibold">₹{parseFloat(assignment.total_paid || 0).toLocaleString()}</span>
                          <span className="text-gray-400"> paid</span>
                        </p>
                      </div>
                      <ChevronRight className="text-gray-400" size={20} />
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===== SCHEDULES TAB ===== */}
        {activeTab === 'schedules' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
              <h3 className="font-bold text-lg text-gray-900 mb-2">Payment Schedules</h3>
              <p className="text-gray-500 text-sm mb-6">
                Different payment plans available for students (Quarterly, Half-Yearly, Annual, etc.)
              </p>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {schedules.map(schedule => (
                  <div key={schedule.id} className={`p-5 rounded-xl border-2 ${
                    schedule.is_default ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 bg-white'
                  }`}>
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-bold text-gray-900">{schedule.name}</h4>
                        <p className="text-xs text-gray-500 mt-1">{schedule.schedule_type_display}</p>
                      </div>
                      {schedule.is_default && (
                        <span className="bg-emerald-500 text-white text-[10px] font-bold px-2 py-1 rounded-full">
                          DEFAULT
                        </span>
                      )}
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Installments/Year</span>
                        <span className="font-semibold text-gray-900">{schedule.installments_per_year}</span>
                      </div>
                      {schedule.discount_percentage > 0 && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Discount</span>
                          <span className="font-semibold text-emerald-600">{schedule.discount_percentage}%</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ===== PAYMENT MODAL ===== */}
      {showPaymentModal && selectedInvoice && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl w-full max-w-md overflow-hidden shadow-2xl animate-in zoom-in-95 duration-200">
            
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-emerald-500 to-teal-600 px-6 py-5 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                    <CreditCard size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg">Record Payment</h3>
                    <p className="text-emerald-100 text-sm">{selectedInvoice.invoice_number}</p>
                  </div>
                </div>
                <button 
                  onClick={() => setShowPaymentModal(false)} 
                  className="p-2 hover:bg-white/20 rounded-xl transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-5">
              
              {/* Student Info */}
              <div className="bg-gray-50 p-4 rounded-xl">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                    {selectedInvoice.student_name?.[0]}
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">{selectedInvoice.student_name}</p>
                    <p className="text-xs text-gray-500 font-mono">{selectedInvoice.student_suid}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                  <span className="text-gray-600">Balance Due</span>
                  <span className="text-2xl font-bold text-red-600">₹{parseFloat(selectedInvoice.balance_due).toLocaleString()}</span>
                </div>
              </div>

              {/* Payment Form */}
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">Amount to Collect</label>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 font-bold text-lg">₹</span>
                    <input 
                      type="number" 
                      className="w-full pl-10 p-4 bg-gray-50 border-2 border-gray-200 rounded-xl font-bold text-2xl outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
                      value={paymentForm.amount}
                      onChange={e => setPaymentForm({...paymentForm, amount: e.target.value})}
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">Payment Mode</label>
                    <select 
                      className="w-full p-3.5 bg-gray-50 border-2 border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-emerald-500 font-medium"
                      value={paymentForm.mode}
                      onChange={e => setPaymentForm({...paymentForm, mode: e.target.value})}
                    >
                      <option value="CASH">💵 Cash</option>
                      <option value="UPI">📱 UPI / Online</option>
                      <option value="CHEQUE">📝 Cheque</option>
                      <option value="BANK_TRANSFER">🏦 Bank Transfer</option>
                      <option value="CARD">💳 Card</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-2 uppercase tracking-wide">Reference ID</label>
                    <input 
                      type="text" 
                      placeholder="Transaction ID"
                      className="w-full p-3.5 bg-gray-50 border-2 border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-emerald-500"
                      value={paymentForm.reference}
                      onChange={e => setPaymentForm({...paymentForm, reference: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <button 
                onClick={handleRecordPayment}
                disabled={paymentLoading || !paymentForm.amount}
                className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold rounded-xl hover:shadow-lg hover:shadow-emerald-200 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {paymentLoading ? (
                  <><Loader2 className="animate-spin" size={20} /> Processing...</>
                ) : (
                  <><CheckCircle size={20} /> Confirm Payment</>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
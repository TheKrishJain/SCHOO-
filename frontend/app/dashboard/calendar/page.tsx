'use client';

import { useState, useEffect, useRef } from 'react';
import api from '@/lib/api';
import { 
  Calendar, ChevronLeft, ChevronRight, Plus, X, Loader2, 
  BookOpen, PartyPopper, AlertCircle, Clock, Trash2,
  GraduationCap, Sun, Flag
} from 'lucide-react';

interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  type: 'exam' | 'holiday' | 'event';
  description?: string;
  color?: string;
  grade_name?: string;
  subject_name?: string;
}

interface Exam {
  id: string;
  name: string;
  exam_date: string;
  subject_name?: string;
  grade_name?: string;
  section_name?: string;
}

interface Holiday {
  id: string;
  name: string;
  date: string;
  description?: string;
}

interface SchoolEvent {
  id: string;
  title: string;
  event_date: string;
  description?: string;
  event_type?: string;
}

export default function SchoolCalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; date: string } | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [addType, setAddType] = useState<'holiday' | 'event'>('holiday');
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    date: '',
    description: '',
  });

  const contextMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchEvents();
    
    // Close context menu on click outside
    const handleClickOutside = (e: MouseEvent) => {
      if (contextMenuRef.current && !contextMenuRef.current.contains(e.target as Node)) {
        setContextMenu(null);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const [examsRes, holidaysRes, eventsRes] = await Promise.all([
        api.get('/academics/exams/'),
        api.get('/schools/holidays/').catch(() => ({ data: [] })),
        api.get('/schools/events/').catch(() => ({ data: [] }))
      ]);

      const exams = Array.isArray(examsRes.data) ? examsRes.data : examsRes.data.results || [];
      const holidays = Array.isArray(holidaysRes.data) ? holidaysRes.data : holidaysRes.data.results || [];
      const schoolEvents = Array.isArray(eventsRes.data) ? eventsRes.data : eventsRes.data.results || [];

      const allEvents: CalendarEvent[] = [
        ...exams.map((e: Exam) => ({
          id: `exam-${e.id}`,
          title: e.name,
          date: e.exam_date,
          type: 'exam' as const,
          description: `${e.subject_name || ''} - ${e.section_name || ''}`,
          grade_name: e.grade_name,
          subject_name: e.subject_name,
          color: 'blue'
        })),
        ...holidays.map((h: Holiday) => ({
          id: `holiday-${h.id}`,
          title: h.name,
          date: h.date,
          type: 'holiday' as const,
          description: h.description,
          color: 'red'
        })),
        ...schoolEvents.map((e: SchoolEvent) => ({
          id: `event-${e.id}`,
          title: e.title,
          date: e.event_date,
          type: 'event' as const,
          description: e.description,
          color: 'green'
        }))
      ];

      setEvents(allEvents);
    } catch (error) {
      console.error('Failed to load calendar events', error);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();

    const days: { date: Date; isCurrentMonth: boolean }[] = [];

    for (let i = startingDay - 1; i >= 0; i--) {
      days.push({ date: new Date(year, month, -i), isCurrentMonth: false });
    }

    for (let i = 1; i <= daysInMonth; i++) {
      days.push({ date: new Date(year, month, i), isCurrentMonth: true });
    }

    const remaining = 42 - days.length;
    for (let i = 1; i <= remaining; i++) {
      days.push({ date: new Date(year, month + 1, i), isCurrentMonth: false });
    }

    return days;
  };

  const formatDateStr = (date: Date) => date.toISOString().split('T')[0];

  const getEventsOnDate = (dateStr: string) => events.filter(e => e.date === dateStr);

  const handleRightClick = (e: React.MouseEvent, dateStr: string) => {
    e.preventDefault();
    setContextMenu({ x: e.clientX, y: e.clientY, date: dateStr });
  };

  const handleAddFromContext = (type: 'holiday' | 'event' | 'exam') => {
    if (type === 'exam') {
      // Navigate to exams page
      window.location.href = '/dashboard/academics/exams';
    } else {
      setAddType(type);
      setFormData({ title: '', date: contextMenu?.date || '', description: '' });
      setShowAddModal(true);
    }
    setContextMenu(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      if (addType === 'holiday') {
        await api.post('/schools/holidays/', {
          name: formData.title,
          date: formData.date,
          description: formData.description
        });
      } else {
        await api.post('/schools/events/', {
          title: formData.title,
          event_date: formData.date,
          description: formData.description
        });
      }
      setShowAddModal(false);
      setFormData({ title: '', date: '', description: '' });
      fetchEvents();
    } catch (error) {
      console.error('Failed to create', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (event: CalendarEvent) => {
    if (!confirm(`Delete "${event.title}"?`)) return;
    
    try {
      const [type, id] = event.id.split('-');
      if (type === 'holiday') {
        await api.delete(`/schools/holidays/${id}/`);
      } else if (type === 'event') {
        await api.delete(`/schools/events/${id}/`);
      }
      fetchEvents();
    } catch (error) {
      console.error('Failed to delete', error);
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'exam': return <GraduationCap size={12} />;
      case 'holiday': return <Sun size={12} />;
      case 'event': return <Flag size={12} />;
      default: return <Calendar size={12} />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'exam': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'holiday': return 'bg-red-100 text-red-700 border-red-200';
      case 'event': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-700 text-white p-6 rounded-2xl shadow-lg">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold mb-1 flex items-center gap-3">
              <Calendar size={28} /> School Calendar
            </h1>
            <p className="text-purple-100">View exams, holidays & events • Right-click to add</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => { setAddType('holiday'); setFormData({ title: '', date: formatDateStr(new Date()), description: '' }); setShowAddModal(true); }}
              className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg font-medium flex items-center gap-2"
            >
              <Sun size={18} /> Add Holiday
            </button>
            <button
              onClick={() => { setAddType('event'); setFormData({ title: '', date: formatDateStr(new Date()), description: '' }); setShowAddModal(true); }}
              className="bg-white text-purple-600 px-4 py-2 rounded-lg font-semibold hover:bg-purple-50 flex items-center gap-2"
            >
              <Plus size={18} /> Add Event
            </button>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 flex gap-6 flex-wrap">
        <span className="flex items-center gap-2 text-sm">
          <span className="w-4 h-4 bg-blue-100 border border-blue-300 rounded"></span>
          <span className="text-gray-700 dark:text-gray-300">Exams</span>
        </span>
        <span className="flex items-center gap-2 text-sm">
          <span className="w-4 h-4 bg-red-100 border border-red-300 rounded"></span>
          <span className="text-gray-700 dark:text-gray-300">Holidays</span>
        </span>
        <span className="flex items-center gap-2 text-sm">
          <span className="w-4 h-4 bg-green-100 border border-green-300 rounded"></span>
          <span className="text-gray-700 dark:text-gray-300">Events</span>
        </span>
        <span className="text-sm text-gray-500 ml-auto">💡 Right-click on any date to add</span>
      </div>

      {/* Calendar */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        {/* Calendar Header */}
        <div className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
            className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg"
          >
            <ChevronLeft size={24} />
          </button>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </h2>
          <button
            onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
            className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg"
          >
            <ChevronRight size={24} />
          </button>
        </div>

        {/* Weekday Headers */}
        <div className="grid grid-cols-7 bg-gray-50 dark:bg-gray-900">
          {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map(day => (
            <div key={day} className="p-3 text-center text-sm font-semibold text-gray-600 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Days */}
        <div className="grid grid-cols-7">
          {getDaysInMonth(currentMonth).map((day, idx) => {
            const dateStr = formatDateStr(day.date);
            const dayEvents = getEventsOnDate(dateStr);
            const isToday = formatDateStr(new Date()) === dateStr;
            const isSelected = selectedDate === dateStr;

            return (
              <div
                key={idx}
                onClick={() => setSelectedDate(dateStr)}
                onContextMenu={(e) => handleRightClick(e, dateStr)}
                className={`min-h-[100px] p-2 border-b border-r border-gray-100 dark:border-gray-700 cursor-pointer transition ${
                  !day.isCurrentMonth ? 'bg-gray-50 dark:bg-gray-900/50' :
                  isSelected ? 'bg-purple-50 dark:bg-purple-900/20' :
                  isToday ? 'bg-blue-50 dark:bg-blue-900/20' :
                  'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                }`}
              >
                <div className={`text-sm font-medium mb-1 ${
                  !day.isCurrentMonth ? 'text-gray-400' :
                  isToday ? 'text-blue-600 font-bold' :
                  'text-gray-900 dark:text-white'
                }`}>
                  {day.date.getDate()}
                  {isToday && <span className="ml-1 text-xs">(Today)</span>}
                </div>

                <div className="space-y-1">
                  {dayEvents.slice(0, 3).map((event, i) => (
                    <div
                      key={i}
                      className={`text-xs px-1.5 py-0.5 rounded truncate border flex items-center gap-1 ${getEventColor(event.type)}`}
                      title={`${event.title}${event.description ? ` - ${event.description}` : ''}`}
                    >
                      {getEventIcon(event.type)}
                      <span className="truncate">{event.title}</span>
                    </div>
                  ))}
                  {dayEvents.length > 3 && (
                    <div className="text-xs text-gray-500 pl-1">+{dayEvents.length - 3} more</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Date Details */}
      {selectedDate && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
            {new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
          </h3>
          
          {getEventsOnDate(selectedDate).length === 0 ? (
            <p className="text-gray-500 text-sm">No events scheduled for this date</p>
          ) : (
            <div className="space-y-2">
              {getEventsOnDate(selectedDate).map((event, i) => (
                <div key={i} className={`p-3 rounded-lg border ${getEventColor(event.type)} flex items-start justify-between`}>
                  <div className="flex items-start gap-2">
                    {getEventIcon(event.type)}
                    <div>
                      <p className="font-medium">{event.title}</p>
                      {event.description && <p className="text-sm opacity-75">{event.description}</p>}
                      <p className="text-xs opacity-60 capitalize mt-1">{event.type}</p>
                    </div>
                  </div>
                  {event.type !== 'exam' && (
                    <button
                      onClick={() => handleDelete(event)}
                      className="p-1 hover:bg-white/50 rounded"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Context Menu */}
      {contextMenu && (
        <div
          ref={contextMenuRef}
          className="fixed bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50 min-w-[180px]"
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          <div className="px-3 py-1 text-xs text-gray-500 border-b border-gray-100 dark:border-gray-700 mb-1">
            {new Date(contextMenu.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          </div>
          <button
            onClick={() => handleAddFromContext('exam')}
            className="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 text-sm"
          >
            <GraduationCap size={16} className="text-blue-600" /> Add Exam
          </button>
          <button
            onClick={() => handleAddFromContext('holiday')}
            className="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 text-sm"
          >
            <Sun size={16} className="text-red-600" /> Add Holiday
          </button>
          <button
            onClick={() => handleAddFromContext('event')}
            className="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 text-sm"
          >
            <Flag size={16} className="text-green-600" /> Add Event
          </button>
        </div>
      )}

      {/* Add Holiday/Event Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl max-w-md w-full">
            <div className={`p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center rounded-t-xl ${
              addType === 'holiday' ? 'bg-gradient-to-r from-red-500 to-orange-500' : 'bg-gradient-to-r from-green-500 to-emerald-500'
            } text-white`}>
              <h2 className="text-lg font-semibold flex items-center gap-2">
                {addType === 'holiday' ? <Sun size={20} /> : <Flag size={20} />}
                Add {addType === 'holiday' ? 'Holiday' : 'Event'}
              </h2>
              <button onClick={() => setShowAddModal(false)} className="text-white/80 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {addType === 'holiday' ? 'Holiday Name' : 'Event Title'} *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  required
                  placeholder={addType === 'holiday' ? 'e.g., Republic Day' : 'e.g., Annual Sports Day'}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Date *
                </label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                  required
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  rows={2}
                  placeholder="Optional description..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className={`flex-1 px-4 py-2 text-white rounded-lg flex items-center justify-center gap-2 ${
                    addType === 'holiday' ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : `Add ${addType === 'holiday' ? 'Holiday' : 'Event'}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

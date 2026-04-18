'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { Plus, Loader2, Users, BookOpen, Calendar, CheckCircle, XCircle } from 'lucide-react';
import Modal from '@/components/Modal';

export default function EnrollmentsPage() {
  const [enrollments, setEnrollments] = useState<any[]>([]);
  const [students, setStudents] = useState<any[]>([]);
  const [grades, setGrades] = useState<any[]>([]);
  const [sections, setSections] = useState<any[]>([]);
  const [academicYears, setAcademicYears] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('ACTIVE');

  useEffect(() => {
    fetchData();
  }, [filter]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [enrollmentsRes, studentsRes, gradesRes, sectionsRes, yearsRes] = await Promise.all([
        api.get(`/enrollments/?status=${filter}`),
        api.get('/students/'),
        api.get('/academics/grades/'),
        api.get('/academics/sections/'),
        api.get('/enrollments/academic-years/')
      ]);
      setEnrollments(enrollmentsRes.data);
      setStudents(studentsRes.data);
      setGrades(gradesRes.data);
      setSections(sectionsRes.data);
      setAcademicYears(yearsRes.data);
    } catch (error) {
      console.error('Failed to load data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: Record<string, string | number | boolean>) => {
    setSubmitting(true);
    setError('');
    try {
      // Find the academic year label from ID
      const selectedYear = academicYears.find(y => y.id === Number(data.academic_year));
      const yearLabel = selectedYear?.year_label || '2025-2026';
      
      // Find grade and section names
      const selectedGrade = grades.find(g => g.id === Number(data.grade));
      const selectedSection = sections.find(s => s.id === Number(data.section));
      
      await api.post('/enrollments/', {
        student: Number(data.student),
        academic_year: yearLabel, // Send as string like "2025-2026"
        grade: selectedGrade?.grade_number?.toString() || String(data.grade), // Send as string like "10"
        section: selectedSection?.section_letter || String(data.section), // Send as string like "A"
        enrollment_date: data.enrollment_date || new Date().toISOString().split('T')[0],
        status: 'ACTIVE'
      });
      setShowModal(false);
      fetchData();
    } catch (err: any) {
      console.error('Enrollment error:', err.response?.data);
      setError(err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Failed to create enrollment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusChange = async (enrollmentId: number, newStatus: string) => {
    try {
      await api.patch(`/enrollments/${enrollmentId}/`, { status: newStatus });
      fetchData();
    } catch (error) {
      console.error('Failed to update enrollment status', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      ACTIVE: 'bg-green-100 text-green-800',
      COMPLETED: 'bg-blue-100 text-blue-800',
      WITHDRAWN: 'bg-red-100 text-red-800',
      TRANSFERRED: 'bg-orange-100 text-orange-800'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Enrollments</h1>
          <p className="text-gray-600 mt-1">Assign students to grades/sections • Note: New students are auto-enrolled when added</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
        >
          <Plus size={18} />
          New Enrollment
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="text-green-600" size={20} />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {enrollments.filter(e => e.status === 'ACTIVE').length}
              </div>
              <div className="text-sm text-gray-600">Active</div>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <BookOpen className="text-blue-600" size={20} />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {enrollments.filter(e => e.status === 'COMPLETED').length}
              </div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <XCircle className="text-red-600" size={20} />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {enrollments.filter(e => e.status === 'WITHDRAWN').length}
              </div>
              <div className="text-sm text-gray-600">Withdrawn</div>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Users className="text-orange-600" size={20} />
            </div>
            <div>
              <div className="text-2xl font-bold">
                {enrollments.filter(e => e.status === 'TRANSFERRED').length}
              </div>
              <div className="text-sm text-gray-600">Transferred</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-3">
        {['ACTIVE', 'COMPLETED', 'WITHDRAWN', 'TRANSFERRED'].map(status => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filter === status
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {status}
          </button>
        ))}
      </div>

      {/* Enrollments List */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Grade</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Section</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Academic Year</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Enrollment Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {enrollments.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                  No enrollments found
                </td>
              </tr>
            ) : (
              enrollments.map((enrollment) => (
                <tr key={enrollment.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">
                      {enrollment.student_name || `Student ID: ${enrollment.student}`}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {enrollment.grade_name || enrollment.grade}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {enrollment.section_name || enrollment.section}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {enrollment.academic_year_name || enrollment.academic_year}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {new Date(enrollment.enrollment_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusBadge(enrollment.status)}`}>
                      {enrollment.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {enrollment.status === 'ACTIVE' && (
                      <select
                        onChange={(e) => handleStatusChange(enrollment.id, e.target.value)}
                        className="text-sm border border-gray-300 rounded px-2 py-1"
                        defaultValue=""
                      >
                        <option value="" disabled>Change Status</option>
                        <option value="COMPLETED">Complete</option>
                        <option value="WITHDRAWN">Withdraw</option>
                        <option value="TRANSFERRED">Transfer</option>
                      </select>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <Modal
          title="Enroll Student in Class"
          onClose={() => setShowModal(false)}
          fields={[
            {
              name: 'student',
              label: 'Select Student',
              type: 'select',
              required: true,
              options: students.map(s => ({
                value: s.id,
                label: `${s.full_name || `${s.first_name} ${s.last_name}`} (${s.suid})`
              }))
            },
            {
              name: 'academic_year',
              label: 'Academic Year',
              type: 'select',
              required: true,
              options: academicYears.map(y => ({
                value: y.id,
                label: `${y.year_label} (${y.start_date} - ${y.end_date})`
              }))
            },
            {
              name: 'grade',
              label: 'Grade/Class',
              type: 'select',
              required: true,
              options: grades.map(g => ({
                value: g.id,
                label: `Grade ${g.grade_number} - ${g.name}`
              }))
            },
            {
              name: 'section',
              label: 'Section',
              type: 'select',
              required: true,
              options: sections.map(s => ({
                value: s.id,
                label: `Section ${s.section_letter} (Grade ${s.grade_name})`
              }))
            },
            {
              name: 'enrollment_date',
              label: 'Enrollment Date (optional)',
              type: 'date',
              required: false,
              placeholder: new Date().toISOString().split('T')[0]
            }
          ]}
          onSubmit={handleSubmit}
          submitLabel="Enroll Student"
          loading={submitting}
          error={error}
        />
      )}
    </div>
  );
}

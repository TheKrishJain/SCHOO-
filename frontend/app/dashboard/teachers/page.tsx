'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { Plus, Loader2, UserCheck, Users, Briefcase, Award, Edit } from 'lucide-react';
import Modal from '@/components/Modal';
import PermissionGate from '@/components/PermissionGate';
import { useResourcePermissions } from '@/lib/rbac-context';
import FeatureGuard from '@/components/FeatureGuard';

export default function TeachersPage() {
  const [teachers, setTeachers] = useState<any[]>([]);
  const [associations, setAssociations] = useState<any[]>([]);
  const [assignments, setAssignments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showOnboardModal, setShowOnboardModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedTeacher, setSelectedTeacher] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('all'); // all, assignments

  // RBAC Permissions
  const { canCreate, canEdit, canDelete } = useResourcePermissions('teachers', 'teacher');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [teachersRes, associationsRes, assignmentsRes] = await Promise.all([
        api.get('/teachers/profiles/'),
        api.get('/teachers/associations/?status=ACTIVE'),
        api.get('/teachers/assignments/?is_active=true')
      ]);
      setTeachers(teachersRes.data);
      setAssociations(associationsRes.data);
      setAssignments(assignmentsRes.data);
    } catch (error) {
      console.error('Failed to load data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOnboard = async (data: Record<string, string | number | boolean>) => {
    setSubmitting(true);
    setError('');
    try {
      alert('Teacher onboarding initiated! (Full implementation requires user creation flow)');
      setShowOnboardModal(false);
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to onboard teacher');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAssign = async (data: Record<string, string | number | boolean>) => {
    setSubmitting(true);
    setError('');
    try {
      await api.post('/teachers/assignments/', {
        teacher: selectedTeacher?.id,
        school: 1,
        role: data.role,
        grade: data.grade || '',
        section: data.section || '',
        subject: data.subject || '',
        academic_year: '2025-2026',
        is_active: true,
      });
      setShowAssignModal(false);
      setSelectedTeacher(null);
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to assign teacher');
    } finally {
      setSubmitting(false);
    }
  };

  const onboardFields = [
    { name: 'full_name', label: 'Full Legal Name', type: 'text' as const, required: true },
    { name: 'email', label: 'Email', type: 'text' as const, required: true },
    { name: 'phone', label: 'Phone', type: 'text' as const, required: true },
    { name: 'date_of_birth', label: 'Date of Birth', type: 'text' as const, required: true, placeholder: 'YYYY-MM-DD' },
    {
      name: 'gender',
      label: 'Gender',
      type: 'select' as const,
      required: true,
      options: [
        { value: 'M', label: 'Male' },
        { value: 'F', label: 'Female' },
        { value: 'O', label: 'Other' }
      ]
    },
    { name: 'qualifications', label: 'Qualifications', type: 'textarea' as const, required: true, placeholder: 'e.g., MSc Math, B.Ed' },
    { name: 'certified_subjects', label: 'Certified Subjects', type: 'textarea' as const, required: true, placeholder: 'Mathematics, Physics' },
    { name: 'experience_years', label: 'Years of Experience', type: 'number' as const, required: true },
  ];

  const assignFields = [
    {
      name: 'role',
      label: 'Role',
      type: 'select' as const,
      required: true,
      options: [
        { value: 'SUBJECT_TEACHER', label: 'Subject Teacher' },
        { value: 'CLASS_TEACHER', label: 'Class Teacher' },
        { value: 'EXAM_INVIGILATOR', label: 'Exam Invigilator' },
        { value: 'SPORTS_TEACHER', label: 'Sports Teacher' },
      ]
    },
    { name: 'subject', label: 'Subject', type: 'text' as const, placeholder: 'e.g., Mathematics' },
    { name: 'grade', label: 'Grade', type: 'text' as const, placeholder: 'e.g., 10' },
    { name: 'section', label: 'Section', type: 'text' as const, placeholder: 'e.g., A' },
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center p-12">
        <Loader2 className="animate-spin text-blue-600" size={40} />
      </div>
    );
  }

  const activeTeachers = associations.filter(a => a.status === 'ACTIVE');

  return (
    <FeatureGuard feature="TEACHERS">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">👩‍🏫 Teacher Management</h1>
            <p className="text-gray-600 mt-1">Global TUID System • School-scoped Assignments</p>
          </div>
          {canCreate && (
            <button
              onClick={() => setShowOnboardModal(true)}
              className="bg-black hover:bg-gray-800 text-white px-6 py-2 rounded-lg font-medium transition flex items-center gap-2"
            >
              <Plus size={20} /> Request Onboarding
            </button>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users size={24} className="text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Teachers</p>
                <p className="text-2xl font-bold text-gray-900">{teachers.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <UserCheck size={24} className="text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Active</p>
                <p className="text-2xl font-bold text-gray-900">{activeTeachers.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Briefcase size={24} className="text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Assignments</p>
                <p className="text-2xl font-bold text-gray-900">{assignments.length}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl border border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-orange-100 rounded-lg">
                <Award size={24} className="text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Verified</p>
                <p className="text-2xl font-bold text-gray-900">
                  {teachers.filter(t => t.verification_status === 'VERIFIED').length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex gap-6">
            <button
              onClick={() => setActiveTab('all')}
              className={`pb-3 px-2 font-medium transition ${activeTab === 'all'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              All Teachers
            </button>
            <button
              onClick={() => setActiveTab('assignments')}
              className={`pb-3 px-2 font-medium transition ${activeTab === 'assignments'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              Assignments
            </button>
          </div>
        </div>

        {/* All Teachers Tab */}
        {activeTab === 'all' && (
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">TUID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subjects</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Experience</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {teachers.map((teacher) => {
                    const association = associations.find(a => a.teacher === teacher.id && a.status === 'ACTIVE');
                    return (
                      <tr key={teacher.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="text-xs font-mono font-bold text-blue-600 break-all max-w-[120px]">{teacher.tuid}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center text-white font-bold">
                              {teacher.full_name?.charAt(0) || 'T'}
                            </div>
                            <div>
                              <div className="font-bold text-gray-900">{teacher.full_name}</div>
                              <div className="text-sm text-gray-500">{teacher.qualifications?.split(',')[0]}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-700">{teacher.certified_subjects?.split(',').slice(0, 2).join(', ')}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-700">{teacher.experience_years} years</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {association ? (
                            <span className="px-3 py-1 text-xs font-bold rounded-full bg-green-100 text-green-700">
                              ACTIVE
                            </span>
                          ) : (
                            <span className="px-3 py-1 text-xs font-bold rounded-full bg-gray-100 text-gray-600">
                              INACTIVE
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {canEdit ? (
                            <button
                              onClick={() => {
                                setSelectedTeacher(teacher);
                                setShowAssignModal(true);
                              }}
                              className="text-blue-600 hover:text-blue-800 font-medium text-sm flex items-center gap-1"
                            >
                              <Edit size={16} /> Assign Role
                            </button>
                          ) : (
                            <span className="text-gray-400 text-sm">—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Assignments Tab */}
        {activeTab === 'assignments' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {assignments.map((assignment) => (
              <div key={assignment.id} className="bg-white p-6 rounded-xl border border-gray-200 hover:border-blue-300 transition">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-400 rounded-full flex items-center justify-center text-white font-bold text-lg">
                      {assignment.teacher_name?.charAt(0) || 'T'}
                    </div>
                    <div>
                      <div className="font-bold text-gray-900">{assignment.teacher_name}</div>
                      <div className="text-xs text-gray-500 font-mono">{assignment.teacher_tuid}</div>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase px-2 py-1 rounded bg-blue-100 text-blue-700">
                      {assignment.role.replace('_', ' ')}
                    </span>
                  </div>

                  {assignment.subject && (
                    <div className="text-sm text-gray-700">
                      <strong>Subject:</strong> {assignment.subject}
                    </div>
                  )}

                  {assignment.grade && (
                    <div className="text-sm text-gray-700">
                      <strong>Class:</strong> {assignment.grade}-{assignment.section}
                    </div>
                  )}

                  <div className="text-xs text-gray-500 mt-2">
                    Academic Year: {assignment.academic_year}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <Modal
          isOpen={showOnboardModal}
          onClose={() => setShowOnboardModal(false)}
          title="Request Teacher Onboarding"
          fields={onboardFields}
          onSubmit={handleOnboard}
          loading={submitting}
          error={error}
          submitButtonText="Submit Request"
          color="indigo"
        />

        {showAssignModal && selectedTeacher && (
          <Modal
            isOpen={showAssignModal}
            onClose={() => {
              setShowAssignModal(false);
              setSelectedTeacher(null);
            }}
            title={`Assign Role to ${selectedTeacher.full_name}`}
            fields={assignFields}
            onSubmit={handleAssign}
            loading={submitting}
            error={error}
            submitButtonText="Assign"
            color="purple"
          />
        )}
      </div>
    </FeatureGuard>
  );
}

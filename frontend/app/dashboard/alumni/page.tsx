'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { GraduationCap, Search, UserPlus, Calendar, Award, TrendingUp } from 'lucide-react';

interface AlumniStudent {
  id: string;
  student_name: string;
  student_suid: string;
  grade: string;
  section: string;
  academic_year: string;
  status: string;
  enrollment_date: string;
}

export default function AlumniPage() {
  const [alumni, setAlumni] = useState<AlumniStudent[]>([]);
  const [filteredAlumni, setFilteredAlumni] = useState<AlumniStudent[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState('all');

  useEffect(() => {
    fetchAlumni();
  }, []);

  useEffect(() => {
    filterAlumni();
  }, [searchTerm, selectedYear, alumni]);

  const fetchAlumni = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        'http://localhost:8000/api/v1/enrollments/student-enrollments/?status=GRADUATED',
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAlumni(response.data);
      setFilteredAlumni(response.data);
    } catch (error) {
      console.error('Failed to fetch alumni', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAlumni = () => {
    let filtered = [...alumni];
    
    if (searchTerm) {
      filtered = filtered.filter(a => 
        a.student_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.student_suid?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (selectedYear !== 'all') {
      filtered = filtered.filter(a => a.academic_year === selectedYear);
    }
    
    setFilteredAlumni(filtered);
  };

  const handleReEnroll = async (studentId: string) => {
    if (!window.confirm('Re-enroll this student? They will be marked as ACTIVE and assigned to a new grade.')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `http://localhost:8000/api/v1/enrollments/student-enrollments/${studentId}/re_enroll/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Student re-enrolled successfully!');
      fetchAlumni();
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.error || 'Failed to re-enroll'}`);
    }
  };

  const graduationYears = [...new Set(alumni.map(a => a.academic_year))].sort().reverse();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-600">Loading alumni...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <GraduationCap className="h-8 w-8 text-purple-600" />
          <h1 className="text-3xl font-bold text-gray-900">Alumni Management</h1>
        </div>
        <p className="text-gray-600">Manage graduated students and track alumni records</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-purple-50 p-6 rounded-xl border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <GraduationCap className="h-8 w-8 text-purple-600" />
            <TrendingUp className="h-5 w-5 text-purple-500" />
          </div>
          <div className="text-3xl font-bold text-purple-700">{alumni.length}</div>
          <div className="text-purple-600 text-sm">Total Alumni</div>
        </div>

        <div className="bg-blue-50 p-6 rounded-xl border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <Calendar className="h-8 w-8 text-blue-600" />
          </div>
          <div className="text-3xl font-bold text-blue-700">{graduationYears.length}</div>
          <div className="text-blue-600 text-sm">Graduation Batches</div>
        </div>

        <div className="bg-green-50 p-6 rounded-xl border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <Award className="h-8 w-8 text-green-600" />
          </div>
          <div className="text-3xl font-bold text-green-700">
            {graduationYears.length > 0 ? graduationYears[0] : 'N/A'}
          </div>
          <div className="text-green-600 text-sm">Latest Batch</div>
        </div>

        <div className="bg-indigo-50 p-6 rounded-xl border border-indigo-200">
          <div className="flex items-center justify-between mb-2">
            <UserPlus className="h-8 w-8 text-indigo-600" />
          </div>
          <div className="text-3xl font-bold text-indigo-700">0</div>
          <div className="text-indigo-600 text-sm">Re-enrolled</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or SUID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Years</option>
            {graduationYears.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Alumni Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SUID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Final Grade</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Graduation Year</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAlumni.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                  No alumni found
                </td>
              </tr>
            ) : (
              filteredAlumni.map(alumnus => (
                <tr key={alumnus.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
                        <GraduationCap className="h-5 w-5 text-purple-600" />
                      </div>
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">{alumnus.student_name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {alumnus.student_suid}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {alumnus.grade} {alumnus.section}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {alumnus.academic_year}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => handleReEnroll(alumnus.id)}
                      className="text-indigo-600 hover:text-indigo-900 font-medium"
                    >
                      Re-enroll
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

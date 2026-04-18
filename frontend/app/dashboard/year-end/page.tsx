'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { Calendar, Users } from 'lucide-react';

interface AcademicYear {
  id: number;
  year_code: string;
  start_date: string;
  end_date: string;
  status: 'UPCOMING' | 'ACTIVE' | 'CLOSING' | 'CLOSED';
}

interface StudentHistoryRecord {
  id: string;
  student_id: string;
  student_name: string;
  student_suid: string;
  academic_year: string;
  grade_name: string;
  section_name: string;
  roll_number: number;
  promoted: boolean;
  promoted_to_grade: string | null;
  promotion_remarks: string;
  created_at: string;
}

export default function PromotionHistoryPage() {
  const router = useRouter();
  const [academicYears, setAcademicYears] = useState<AcademicYear[]>([]);
  const [selectedYear, setSelectedYear] = useState<string | null>(null);
  const [historyRecords, setHistoryRecords] = useState<StudentHistoryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [schoolId, setSchoolId] = useState<string | null>(null);

  useEffect(() => {
    const fetchSchoolId = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('http://localhost:8000/api/v1/schools/settings/my_settings/', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSchoolId(response.data.school);
      } catch (error) {
        console.error('Error fetching school ID:', error);
      }
    };
    fetchSchoolId();
    fetchAcademicYears();
  }, []);

  useEffect(() => {
    if (selectedYear && schoolId) {
      fetchAcademicHistory(selectedYear);
    }
  }, [selectedYear, schoolId]);

  const fetchAcademicYears = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/v1/enrollments/academic-years/', {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Deduplicate and sort by start_date descending
      const uniq = new Map<string, AcademicYear>();
      (response.data || []).forEach((y: AcademicYear) => {
        const key = `${y.year_code}:${y.status}`;
        if (!uniq.has(key)) uniq.set(key, y);
      });
      const uniqueYears = Array.from(uniq.values());
      uniqueYears.sort((a, b) => new Date(b.start_date).getTime() - new Date(a.start_date).getTime());

      setAcademicYears(uniqueYears);
      const active = uniqueYears.find((y: AcademicYear) => y.status === 'ACTIVE');
      if (active) setSelectedYear(String(active.id));
    } catch (error) {
      console.error('Error fetching academic years:', error);
    }
  };

  const fetchAcademicHistory = async (yearId: string) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const year = academicYears.find(y => String(y.id) === yearId);

      if (!year || !schoolId) {
        console.log('Missing year or school ID');
        return;
      }

      const response = await axios.get(
        `http://localhost:8000/api/v1/enrollments/promotions/`,
        {
          params: {
            academic_year: year.year_code,
            school: schoolId
          },
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      console.log('History response:', response.data);
      setHistoryRecords(Array.isArray(response.data) ? response.data : []);
    } catch (error: any) {
      console.error('Error fetching history:', error);
      setHistoryRecords([]);
    } finally {
      setLoading(false);
    }
  };

  const activeYear = academicYears.find(y => String(y.id) === String(selectedYear));

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Student Promotion History</h1>
              <p className="text-gray-600 mt-1">View student grade progression across academic years</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex flex-col items-end">
                <label className="text-sm font-medium text-gray-700 mb-1">Academic Year</label>
                <select
                  value={selectedYear || ''}
                  onChange={(e) => setSelectedYear(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-w-[200px]"
                >
                  {academicYears.map((year) => (
                    <option key={year.id} value={year.id}>
                      {year.year_code} ({year.status})
                    </option>
                  ))}
                </select>
              </div>
              {activeYear && (
                <div className="text-right">
                  <div className="text-sm text-gray-600">Status</div>
                  <div className={`font-semibold ${activeYear.status === 'ACTIVE' ? 'text-green-600' :
                    activeYear.status === 'CLOSED' ? 'text-gray-600' : 'text-blue-600'
                    }`}>
                    {activeYear.status}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(activeYear.start_date).toLocaleDateString()} — {new Date(activeYear.end_date).toLocaleDateString()}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* History Table */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">
                Student History for {activeYear?.year_code}
              </h2>
              <span className="ml-auto text-sm text-gray-600">
                {historyRecords.length} students
              </span>
            </div>
          </div>

          <div className="overflow-x-auto">
            {loading ? (
              <div className="p-12 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-gray-600">Loading history...</p>
              </div>
            ) : historyRecords.length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p>No student history found for this academic year</p>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Grade
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Promoted To
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Section
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Roll No
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Remarks
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {historyRecords.map((record) => (
                    <tr
                      key={record.id}
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => router.push(`/dashboard/students/${record.student_id}`)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col">
                          <div className="text-sm font-medium text-gray-900">{record.student_name}</div>
                          <div className="text-xs text-gray-500">{record.student_suid}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{record.grade_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {record.promoted_to_grade ? (
                            <span className="font-medium text-green-700">{record.promoted_to_grade}</span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">Section {record.section_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{record.roll_number}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${record.promoted
                          ? 'bg-green-100 text-green-800'
                          : 'bg-blue-100 text-blue-800'
                          }`}>
                          {record.promoted ? 'Promoted' : 'Current'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600 max-w-xs truncate">
                          {record.promotion_remarks || '-'}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

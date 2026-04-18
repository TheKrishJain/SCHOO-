'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import api from '@/lib/api';
import { ArrowLeft, Save, Loader2, UploadCloud, User } from 'lucide-react';

export default function EditStudentPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Image State
  const [preview, setPreview] = useState<string | null>(null);
  const [photoFile, setPhotoFile] = useState<File | null>(null);

  const [formData, setFormData] = useState({
    first_name: '',
    middle_name: '',
    last_name: '',
    email: '', // Read-only usually, but good to show
    phone_number: '',
    address: '',
    blood_group: '',
    date_of_birth: ''
  });

  useEffect(() => {
    if (id) fetchStudent();
  }, [id]);

  const fetchStudent = async () => {
    try {
      const res = await api.get(`/students/${id}/`);
      const s = res.data;
      
      // Pre-fill form
      setFormData({
        first_name: s.first_name || '', 
        last_name: s.last_name || '',
        middle_name: s.middle_name || '',
        email: s.email || '',
        phone_number: s.phone_number || '',
        address: s.address || '',
        blood_group: s.blood_group || '',
        date_of_birth: s.date_of_birth || ''
      });

      // Set existing photo preview
      if (s.profile_photo) {
        setPreview(s.profile_photo);
      }
      
      setLoading(false);
    } catch (e) {
      alert("Failed to load student data");
    }
  };

  const handleChange = (e: any) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle New Photo Selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPhotoFile(file);
      setPreview(URL.createObjectURL(file)); // Show new preview
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    
    // Use FormData to allow Image Uploads
    const data = new FormData();
    data.append('first_name', formData.first_name);
    data.append('last_name', formData.last_name);
    data.append('middle_name', formData.middle_name);
    data.append('phone_number', formData.phone_number);
    data.append('address', formData.address);
    data.append('blood_group', formData.blood_group);
    data.append('date_of_birth', formData.date_of_birth);

    // Only append photo if a new one was selected
    if (photoFile) {
        data.append('profile_photo', photoFile);
    }

    try {
      // PATCH request to update
      await api.patch(`/students/${id}/`, data);
      alert("Student updated successfully!");
      router.push(`/dashboard/students/${id}`);
    } catch (e) {
      console.error(e);
      alert("Failed to update student.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-20 flex justify-center"><Loader2 className="animate-spin text-gray-400" size={30}/></div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
            <button onClick={() => router.back()} className="p-2 hover:bg-gray-200 rounded-full text-gray-500 transition-colors">
                <ArrowLeft size={20} />
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Edit Student</h1>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 space-y-8 animate-in fade-in duration-300">
            
            {/* PHOTO UPLOAD SECTION */}
            <div className="flex flex-col items-center justify-center">
                <div className="relative w-32 h-32 group cursor-pointer">
                    {preview ? (
                        <img src={preview} alt="Profile" className="w-full h-full object-cover rounded-full border-4 border-gray-100 shadow-sm" />
                    ) : (
                        <div className="w-full h-full bg-gray-100 rounded-full flex items-center justify-center text-gray-400">
                            <User size={40} />
                        </div>
                    )}
                    
                    {/* The Overlay Icon */}
                    <label className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                        <UploadCloud size={24} />
                        <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
                    </label>
                </div>
                <p className="text-xs text-gray-400 mt-3">Click to change photo</p>
            </div>

            {/* FORM FIELDS */}
            <div className="grid md:grid-cols-3 gap-6">
                <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">First Name</label>
                    <input name="first_name" value={formData.first_name} onChange={handleChange} className="w-full p-3 border rounded-lg mt-1 focus:ring-2 focus:ring-blue-500 outline-none" required />
                </div>
                <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Middle Name</label>
                    <input name="middle_name" value={formData.middle_name} onChange={handleChange} className="w-full p-3 border rounded-lg mt-1 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Last Name</label>
                    <input name="last_name" value={formData.last_name} onChange={handleChange} className="w-full p-3 border rounded-lg mt-1 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Email (Read Only)</label>
                    <input name="email" value={formData.email} disabled className="w-full p-3 border rounded-lg mt-1 bg-gray-50 text-gray-500 cursor-not-allowed" />
                </div>
                <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Phone</label>
                    <input name="phone_number" value={formData.phone_number} onChange={handleChange} className="w-full p-3 border rounded-lg mt-1 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
            </div>

            <div>
                <label className="text-xs font-bold text-gray-500 uppercase">Address</label>
                <textarea name="address" rows={3} value={formData.address} onChange={handleChange} className="w-full p-3 border rounded-lg mt-1 focus:ring-2 focus:ring-blue-500 outline-none" />
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                 <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Date of Birth</label>
                    <input type="date" name="date_of_birth" value={formData.date_of_birth} onChange={handleChange} className="w-full p-3 border rounded-lg mt-1 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Blood Group</label>
                    <input name="blood_group" value={formData.blood_group} onChange={handleChange} className="w-full p-3 border rounded-lg mt-1 focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-gray-100">
                <button type="submit" disabled={saving} className="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 flex items-center gap-2 transition-all disabled:opacity-50 shadow-md">
                    {saving ? <Loader2 className="animate-spin" size={20}/> : <Save size={20}/>}
                    Save Changes
                </button>
            </div>

        </form>
      </div>
    </div>
  );
}